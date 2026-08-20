from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import ProtectedError
from django.core.mail import EmailMessage
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import Order, OrderItem, Product, Review, Store


def forbidden(message):
    """Return a 403 Forbidden response with a message and a link
    back to the catalog."""

    return HttpResponseForbidden(
        f'<p>{message}</p><p><a href="/ecommerce/">Back to catalog</a></p>'
    )


def view_product_page(request):
    """Search for and display a single product by name."""

    user = request.user  # Get the current logged-in user

    # Check if user has permission to view products
    if (user.has_perm('eCommerce.view_product')
            or user.has_perm('eCommerce.view_products')):
        if request.method == 'POST':
            # Get product name from form submission
            product_name = request.POST.get('product')

            if not product_name:
                # If no product name given, show error on page
                return render(request, 'eCommerce/product_page.html', {
                    'error': 'No product name was given.'
                })

            try:
                # Try to find the product in the database by its name
                product = Product.objects.get(name=product_name)
                # Show product details on the page
                return render(
                    request, 'eCommerce/product_page.html',
                    {'product': product}
                )
            except ObjectDoesNotExist:
                # If product not found, show error on page
                return render(request, 'eCommerce/product_page.html', {
                    'error': 'Product not found.'
                })
            except Product.MultipleObjectsReturned:
                # Product names are not guaranteed unique across stores
                return render(request, 'eCommerce/product_page.html', {
                    'error': 'Multiple products share that name. '
                             'Try searching from the catalog instead.'
                })
        # If page is opened normally (GET request), just show empty form
        return render(request, 'eCommerce/product_page.html')
    # If user does not have permission to view products, show error
    return render(request, 'eCommerce/product_page.html', {
        'error': 'You do not have permission to view this product.'
    })


def change_product_price(request):
    """Update the price of a product found by name, if the requesting
    vendor owns it."""

    user = request.user

    if (user.has_perm('eCommerce.change_product')
            or user.has_perm('eCommerce.change_products')):
        if request.method == 'POST':
            product_name = request.POST.get('product')
            new_price = request.POST.get('new_price')

            if not product_name or not new_price:
                return render(request, 'eCommerce/change_price.html', {
                    'error': 'Please provide both product name and new '
                             'price.'
                })

            try:
                product = Product.objects.select_related('store').get(
                    name=product_name
                )

                if product.store.owner != user:
                    return render(request, 'eCommerce/change_price.html', {
                        'error': 'You do not have permission to change '
                                 'this product.'
                    })

                product.price = float(new_price)
                product.save()
                return HttpResponseRedirect(
                    reverse('eCommerce:product_page')
                )

            except ValueError:
                return render(request, 'eCommerce/change_price.html', {
                    'error': 'Invalid price format.'
                })
            except ObjectDoesNotExist:
                return render(request, 'eCommerce/change_price.html', {
                    'error': 'Product not found.'
                })
            except Product.MultipleObjectsReturned:
                return render(request, 'eCommerce/change_price.html', {
                    'error':
                    'Multiple products share that name. '
                    'Use the vendor panel to edit a specific one.'
                })

        return render(request, 'eCommerce/change_price.html')

    return render(request, 'eCommerce/change_price.html', {
        'error': 'You do not have permission to change prices.'
    })


def add_item_to_cart(request):
    """Add a product to the current user's session cart, or increase
    its quantity."""

    product_id = request.POST.get('product_id')
    quantity = request.POST.get('quantity')

    if not product_id or not quantity:
        return redirect('eCommerce:main_cart_page')

    try:
        quantity = int(quantity)
        if quantity < 1:
            quantity = 1
    except ValueError:
        quantity = 1

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return redirect('eCommerce:products_list')

    cart = request.session.get('cart', {})
    key = str(product.id)

    if key in cart:
        cart[key] += quantity
    else:
        cart[key] = quantity

    request.session['cart'] = cart
    request.session.modified = True

    return redirect(reverse('eCommerce:main_cart_page'))


def retrieve_products(request):
    """Build a list of products and quantities from the user's
    session cart."""

    products = []
    session = request.session

    if 'cart' in session:
        for product_id, quantity in session['cart'].items():
            try:
                product = Product.objects.select_related('store').get(
                    id=product_id
                )
                products.append({'product': product, 'quantity': quantity})
            except Product.DoesNotExist:
                pass

    return products


@login_required
def show_user_cart(request):
    """Display the current user's cart with subtotals and total price."""
    cart_items = retrieve_products(request)
    total_price = 0

    # Calculate subtotal for each cart item and total price for whole cart
    for item in cart_items:
        subtotal = item['product'].price * item['quantity']
        item['subtotal'] = subtotal  # Add subtotal to item dictionary
        total_price += subtotal

    # Render cart page, passing in items and total price
    return render(request, 'eCommerce/main_cart_page.html', {
        'cart': cart_items,
        'total_price': total_price,
    })


def list_products(request):
    """Display the catalog of all products from every store.

    'is_vendor' isn't set here because it's already injected into every
    template's context by eCommerce.context_processors.user_role.
    """

    products = Product.objects.select_related('store').all()
    return render(request, 'eCommerce/products_list.html', {
        'products': products,
    })


@login_required
def clear_cart(request):
    """Empty the current user's session cart."""
    request.session['cart'] = {}
    request.session.modified = True  # Mark session as changed

    # Redirect to cart page after clearing
    return redirect('eCommerce:main_cart_page')


@login_required
def my_stores(request):
    """Display the stores owned by the current user."""

    if not request.user.has_perm('eCommerce.view_store'):
        return forbidden("You don't have permission to view stores.")
    stores = Store.objects.filter(owner=request.user)
    return render(request, 'eCommerce/my_stores.html', {'stores': stores})


@login_required
def create_store(request):
    """Create a new store owned by the current user."""

    if not request.user.has_perm('eCommerce.add_store'):
        return forbidden("You don't have permission to create stores.")

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        if not name:
            return render(request, 'eCommerce/store_form.html', {
                'error': 'The store name is required.'
            })
        Store.objects.create(
            owner=request.user, name=name, description=description
        )
        return redirect('eCommerce:my_stores')

    return render(request, 'eCommerce/store_form.html')


@login_required
def edit_store(request, store_id):
    """Edit a store owned by the current user."""

    store = get_object_or_404(Store, id=store_id)

    if (store.owner != request.user
            or not request.user.has_perm('eCommerce.change_store')):
        return forbidden("You don't have permission to edit this store.")
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        if not name:
            return render(request, 'eCommerce/store_form.html', {
                'store': store, 'error': 'The store name is required.'
            })
        store.name = name
        store.description = description
        store.save()
        return redirect('eCommerce:my_stores')

    return render(request, 'eCommerce/store_form.html', {'store': store})


@login_required
def delete_store(request, store_id):
    """Delete a store owned by the current user."""

    store = get_object_or_404(Store, id=store_id)

    if (store.owner != request.user
            or not request.user.has_perm('eCommerce.delete_store')):
        return forbidden("You don't have permission to delete this store.")

    if request.method == 'POST':
        try:
            store.delete()
        except ProtectedError:
            return render(request, 'eCommerce/store_confirm_delete.html', {
                'store': store,
                'error': 'This store has products that are part of past '
                         'orders, so it cannot be deleted. Order history '
                         'has to be preserved, so remove or reassign '
                         'those products before deleting the store.',
            })
        return redirect('eCommerce:my_stores')

    return render(
        request, 'eCommerce/store_confirm_delete.html', {'store': store}
    )


@login_required
def store_products(request, store_id):
    """Display the products belonging to a store owned by the
    current user."""

    store = get_object_or_404(Store, id=store_id)

    if store.owner != request.user:
        return forbidden(
            "You don't have permission to view this store's products."
        )

    products = store.products.all()
    return render(request, 'eCommerce/store_products.html', {
        'store': store,
        'products': products,
    })


@login_required
def create_product(request, store_id):
    """Add a new product to a store owned by the current user."""

    store = get_object_or_404(Store, id=store_id)

    if (store.owner != request.user
            or not request.user.has_perm('eCommerce.add_products')):
        return forbidden(
            "You don't have permission to add products to this store."
        )

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        price = request.POST.get('price')
        stock = request.POST.get('stock')

        try:
            price = float(price)
            stock = int(stock)
            if price < 0 or stock < 0:
                raise ValueError
        except (TypeError, ValueError):
            return render(request, 'eCommerce/product_form.html', {
                'store': store,
                'error': 'Price and stock must be valid numbers and not '
                         'negative.',
            })

        if not name:
            return render(request, 'eCommerce/product_form.html', {
                'store': store, 'error': 'The product name is required.'
            })

        store.products.create(
            name=name, description=description, price=price, stock=stock
        )
        return redirect('eCommerce:store_products', store_id=store.id)

    return render(request, 'eCommerce/product_form.html', {'store': store})


@login_required
def edit_product(request, product_id):
    """Edit a product belonging to a store owned by the current user."""

    product = get_object_or_404(Product, id=product_id)

    if (product.store.owner != request.user
            or not request.user.has_perm('eCommerce.change_products')):
        return forbidden("You don't have permission to edit this product.")

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        price = request.POST.get('price')
        stock = request.POST.get('stock')

        try:
            price = float(price)
            stock = int(stock)
            if price < 0 or stock < 0:
                raise ValueError
        except (TypeError, ValueError):
            return render(request, 'eCommerce/product_form.html', {
                'product': product,
                'store': product.store,
                'error': 'Price and stock must be valid numbers and not '
                         'negative.',
            })

        product.name = name
        product.description = description
        product.price = price
        product.stock = stock
        product.save()
        return redirect(
            'eCommerce:store_products', store_id=product.store.id
        )

    return render(request, 'eCommerce/product_form.html', {
        'product': product,
        'store': product.store,
    })


@login_required
def delete_product(request, product_id):
    """Delete a product belonging to a store owned by the current user."""

    product = get_object_or_404(Product, id=product_id)

    if (product.store.owner != request.user
            or not request.user.has_perm('eCommerce.delete_products')):
        return forbidden("You don't have permission to delete this product.")
    if request.method == 'POST':
        store_id = product.store.id
        try:
            product.delete()
        except ProtectedError:
            return render(
                request,
                'eCommerce/product_confirm_delete.html',
                {
                    'product': product,
                    'error': 'This product is part of past orders, so '
                             'it cannot be deleted. Order history has '
                             'to be preserved.',
                },
            )
        return redirect('eCommerce:store_products', store_id=store_id)

    return render(
        request,
        'eCommerce/product_confirm_delete.html',
        {'product': product},
    )


@login_required
def remove_from_cart(request, product_id):
    """Remove a single product from the current user's session cart."""

    cart = request.session.get('cart', {})
    cart.pop(str(product_id), None)
    request.session['cart'] = cart
    request.session.modified = True
    return redirect('eCommerce:main_cart_page')


def product_detail(request, product_id):
    """Display a product's details and reviews, and allow adding it
    to the cart."""

    product = get_object_or_404(
        Product.objects.select_related('store'), id=product_id
    )
    reviews = product.reviews.all().order_by('-created_at')
    return render(request, 'eCommerce/product_detail.html', {
        'product': product,
        'reviews': reviews,
    })


def send_invoice_email(order):
    """Email an invoice listing the items and total for a completed
    order."""

    lines = [
        f"Thank you for your purchase, {order.user.username}.",
        "",
        f"Order #{order.id}",
        "",
    ]
    for item in order.items.all():
        lines.append(
            f"{item.quantity}x {item.product.name} — "
            f"${item.price_at_purchase} each"
        )
    lines.append("")
    lines.append(f"Total: ${order.total}")

    email = EmailMessage(
        subject=f"Factura — Orden #{order.id}",
        body="\n".join(lines),
        from_email="noreply@artisanhub.com",
        to=[order.user.email],
    )
    email.send(fail_silently=True)


@login_required
def process_checkout(request):
    """Validate stock, create an order from the cart, update stock,
    and email an invoice."""

    if request.method != 'POST':
        return redirect('eCommerce:main_cart_page')

    cart = request.session.get('cart', {})
    if not cart:
        return redirect('eCommerce:main_cart_page')

    items_to_process = []
    errors = []

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.select_related('store').get(
                id=product_id
            )
        except Product.DoesNotExist:
            continue
        if product.stock < quantity:
            errors.append(
                f"Not enough stock of '{product.name}' "
                f"(available: {product.stock}, in your cart: {quantity})."
            )
        else:
            items_to_process.append((product, quantity))

    if errors:
        cart_items = retrieve_products(request)
        for item in cart_items:
            item['subtotal'] = item['product'].price * item['quantity']
        total_price = sum(item['subtotal'] for item in cart_items)
        return render(request, 'eCommerce/main_cart_page.html', {
            'cart': cart_items,
            'total_price': total_price,
            'errors': errors,
        })

    total = sum(
        product.price * quantity for product, quantity in items_to_process
    )
    order = Order.objects.create(user=request.user, total=total)

    for product, quantity in items_to_process:
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price_at_purchase=product.price,
        )
        product.stock -= quantity
        product.save()

    request.session['cart'] = {}
    request.session.modified = True

    send_invoice_email(order)

    return redirect('eCommerce:checkout_success', order_id=order.id)


@login_required
def checkout_success(request, order_id):
    """Display a confirmation page for a completed order belonging
    to the current user."""

    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'eCommerce/order_success.html', {'order': order})


@login_required
def my_orders(request):
    """Display the current user's past orders."""

    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'eCommerce/my_orders.html', {'orders': orders})


@login_required
def add_review(request, product_id):
    """Create a review for a product, marked verified if the user
    purchased it."""
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')

        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError
        except (TypeError, ValueError):
            return redirect(
                'eCommerce:product_detail', product_id=product.id
            )

        # A review counts as verified if this user has a real
        # purchase of this product
        verified = OrderItem.objects.filter(
            order__user=request.user, product=product
        ).exists()

        Review.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            comment=comment,
            verified=verified,
        )

    return redirect('eCommerce:product_detail', product_id=product.id)

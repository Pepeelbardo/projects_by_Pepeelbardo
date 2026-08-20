from django.urls import path
from . import views

# Tells Django which app these URLs belong to.
app_name = 'eCommerce'

urlpatterns = [
    # Home page: Shows the list of all products
    path('', views.list_products, name='products_list'),

    # Page to view details about a specific product (with a search form)
    path('product/', views.view_product_page, name='product_page'),

    # Page to change the price of a product (for users with permission)
    path('change-price/', views.change_product_price, name='change_price'),

    # URL to add an item to the shopping cart (usually called by a form)
    path('add-to-cart/', views.add_item_to_cart, name='add_to_cart'),

    # Page showing all items currently in the user's cart with totals
    path('cart/', views.show_user_cart, name='main_cart_page'),

    # URL to clear all items from the user's cart
    path('clear-cart/', views.clear_cart, name='clear_cart'),

    # Page showing all stores owned by the logged-in vendor
    path('vendor/stores/', views.my_stores, name='my_stores'),

    # Page to create a new store (for vendors)
    path('vendor/stores/add/', views.create_store, name='create_store'),

    # Page to edit a store owned by the logged-in vendor
    path(
        'vendor/stores/<int:store_id>/edit/',
        views.edit_store,
        name='edit_store',
    ),

    # Page to confirm and delete a store owned by the logged-in vendor
    path(
        'vendor/stores/<int:store_id>/delete/',
        views.delete_store,
        name='delete_store',
    ),

    # Page listing the products that belong to a specific store
    path(
        'vendor/stores/<int:store_id>/products/',
        views.store_products,
        name='store_products',
    ),

    # Page to add a new product to a specific store
    path(
        'vendor/stores/<int:store_id>/products/add/',
        views.create_product,
        name='create_product',
    ),

    # Page to edit a product owned by the logged-in vendor
    path(
        'vendor/products/<int:product_id>/edit/',
        views.edit_product,
        name='edit_product',
    ),

    # Page to confirm and delete a product owned by the logged-in vendor
    path(
        'vendor/products/<int:product_id>/delete/',
        views.delete_product,
        name='delete_product',
    ),

    # Page showing a product's details and reviews
    path(
        'product/<int:product_id>/',
        views.product_detail,
        name='product_detail',
    ),

    # URL to remove a single product from the user's cart
    path(
        'cart/remove/<int:product_id>/',
        views.remove_from_cart,
        name='remove_from_cart',
    ),

    # URL to confirm the purchase and process checkout
    path(
        'checkout/',
        views.process_checkout,
        name='checkout',
    ),

    # Page confirming a successful order
    path(
        'checkout/success/<int:order_id>/',
        views.checkout_success,
        name='checkout_success',
    ),

    # Page showing the logged-in user's past orders
    path('orders/', views.my_orders, name='my_orders'),

    # URL to submit a review for a product
    path(
        'product/<int:product_id>/review/',
        views.add_review,
        name='add_review',
    ),
]

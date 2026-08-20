from django.apps import apps as global_apps
from django.contrib.auth.management import create_permissions
from django.db import migrations


def create_groups(apps, schema_editor):
    """Create 'Vendors' and 'Buyers' groups with appropriate
    permissions for the eCommerce app."""

    # Permission rows are normally created by Django's post_migrate
    # signal, which only fires after every migration in this run has
    # finished applying — including this one. Since we need to look
    # up the Store/Product Permission rows right now, we force Django
    # to create them for this app first, instead of finding an empty
    # queryset and silently assigning no permissions to the groups.
    create_permissions(global_apps.get_app_config('eCommerce'), verbosity=0)

    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Store = apps.get_model('eCommerce', 'Store')
    Product = apps.get_model('eCommerce', 'Product')

    store_ct = ContentType.objects.get_for_model(Store)
    product_ct = ContentType.objects.get_for_model(Product)

    vendors, _ = Group.objects.get_or_create(name='Vendors')
    buyers, _ = Group.objects.get_or_create(name='Buyers')

    vendor_perms = list(Permission.objects.filter(
        content_type=store_ct,
        codename__in=['add_store', 'change_store', 'delete_store', 'view_store']
    ))
    vendor_perms += list(Permission.objects.filter(
        content_type=product_ct,
        codename__in=[
            'add_products', 'change_products',
            'delete_products', 'view_products'
            ]
    ))
    vendors.permissions.set(vendor_perms)

    buyer_perms = Permission.objects.filter(
        content_type=product_ct,
        codename='view_products')
    buyers.permissions.set(buyer_perms)


def remove_groups(apps, schema_editor):
    """Remove 'Vendors' and 'Buyers' groups from the database."""
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=['Vendors', 'Buyers']).delete()


class Migration(migrations.Migration):
    """Migration to create 'Vendors' and 'Buyers' groups with appropriate permissions
    for the eCommerce app."""

    dependencies = [
        ('eCommerce', '0002_order_orderitem_review_store_product_store'),
    ]

    operations = [
        migrations.RunPython(create_groups, remove_groups),
    ]

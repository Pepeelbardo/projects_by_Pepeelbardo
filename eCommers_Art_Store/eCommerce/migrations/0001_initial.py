from django.db import migrations, models

class Migration(migrations.Migration):
    """Initial migration for the eCommerce app, creating the Product model with fields for name,
    description, price, and stock. Also sets up permissions for product management."""

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("stock", models.PositiveIntegerField()),
            ],
            options={
                "permissions": [
                    ("add_products", "Can add products"),
                    ("change_products", "Can change products"),
                    ("delete_products", "Can delete products"),
                    ("view_products", "Can view products"),
                ],
            },
        ),
    ]

# ArtisanHub (AuthLog) — Django eCommerce Application

A multi-vendor marketplace built with Django. Buyers can browse products from
multiple stores, manage a cart, check out, and leave reviews. Vendors can create
stores and manage their own products. Includes full authentication, role-based
permissions, and password recovery.

## Apps

- **grabsomore** — authentication: register, login, logout, password reset with
  expiring single-use tokens.
- **eCommerce** — stores, products, cart, checkout, orders, and reviews.

## Prerequisites

- Python 3.10+
- MariaDB (or another MySQL-compatible server)
- `pkg-config` and the MySQL client libraries (needed to build `mysqlclient`)

On macOS with Homebrew:

```bash
brew install pkg-config mysql-client mariadb
brew services start mariadb
```

## Getting started

These steps assume you don't have this project on your machine yet — just a
link to the GitHub repository.

### 1. Clone the repository and enter the project folder

This project lives inside the `eCommers_Art_Store` folder of a larger
repository. Clone the repository, then move into that folder:

```bash
git clone https://github.com/Pepeelbardo/projects_by_Pepeelbardo.git
cd projects_by_Pepeelbardo/eCommers_Art_Store
```

Everything below is run from inside this `eCommers_Art_Store` folder (the
one that contains `manage.py`).

### 2. Create and activate a virtual environment

Do this from inside the project folder, so the `venv/` directory is created
alongside the code instead of somewhere else on your machine:

```bash
python3 -m venv venv
source venv/bin/activate
```

If `mysqlclient` fails to build in the next step, export these first
(Homebrew's `mysql-client` is keg-only and not on the default library path):

```bash
export PKG_CONFIG_PATH="/opt/homebrew/opt/mysql-client/lib/pkgconfig"
export LDFLAGS="-L/opt/homebrew/opt/mysql-client/lib"
export CPPFLAGS="-I/opt/homebrew/opt/mysql-client/include"
```

### 3. Install dependencies

Run this from the project folder (where `requirements.txt` lives) — running
it from anywhere else will fail with a "file not found" error:

```bash
pip install -r requirements.txt
```

### 4. Set up your environment variables

Copy the example file and fill in real values. `.env` is not committed to
version control, so this step has to happen after cloning:

```bash
cp .env.example .env
```

Open `.env` and fill in each value. For `SECRET_KEY`, generate a fresh random
one — never reuse the example value or someone else's key. With the virtual
environment active:

```bash
python manage.py shell
```

Then, inside the shell:

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Copy the printed value into `SECRET_KEY` in your `.env`, then exit the shell
with `exit()`.

Your `.env` should end up looking like this (with your own real values):

```
SECRET_KEY=<the value you generated above>
DEBUG=True
DB_NAME=ecommerce_db
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=3306
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

`DB_PORT` defaults to `3306` (the standard MySQL/MariaDB port) if you leave it
out, so you only need to set it if your database runs on a different port.

Using the console email backend prints password-reset and invoice emails to
the terminal instead of sending real emails — useful for local testing.

### 5. Set up the database

Log in to MariaDB as root (on a fresh Homebrew install, root has no password
and uses socket authentication, so use `sudo`):

```bash
sudo mysql -u root
```

Create the database and an application user (use the same values you put in
`.env`):

```sql
CREATE DATABASE ecommerce_db;
CREATE USER 'your-db-user'@'localhost' IDENTIFIED BY 'your-db-password';
GRANT ALL PRIVILEGES ON ecommerce_db.* TO 'your-db-user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 6. Run migrations and start the server

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Applying migrations also creates the `Vendors` and `Buyers` groups with their
default permissions (via a data migration in the `eCommerce` app), so roles
work immediately after a fresh install.

Visit `http://127.0.0.1:8000/` to register or log in, and
`http://127.0.0.1:8000/admin/` to access the Django admin panel with your
superuser account.

## Usage

**Authentication (`grabsomore` app)**

- Register at `/register/`, choosing "Buyer" or "Vendor".
- Log in / out at `/`.
- Request a password reset at `/request-password-reset/`; the reset link
  (printed to the console with the default email backend) expires after 5
  minutes and can only be used once.

**Buyer flow (`eCommerce` app)**

- Browse the catalog at `/ecommerce/`.
- View a product's details, add it to the cart, and leave a review at
  `/ecommerce/product/<id>/`.
- Manage the cart and confirm a purchase at `/ecommerce/cart/`. Checkout
  re-validates stock, creates an order, decreases stock, empties the cart, and
  emails an invoice.
- View past orders at `/ecommerce/orders/`.

**Vendor flow (`eCommerce` app)**

- Manage stores at `/ecommerce/vendor/stores/` (visible only to users in the
  `Vendors` group).
- Manage a store's products at `/ecommerce/vendor/stores/<id>/products/`.
- All edit/delete actions check both the Django permission and store/product
  ownership, so a vendor can only manage their own stores and products.
- The navigation bar only shows links the logged-in user's role is
  authorised to use (e.g. buyers see Cart/My Orders, vendors see My Stores).

## Project structure

```
AuthLog/
├── AuthLog/
│   ├── settings.py          # Project settings (reads DB/email config from .env)
│   ├── urls.py
│   └── wsgi.py
├── templates/
│   └── base.html              # Shared layout: nav bar, styling, page blocks
├── grabsomore/               # Authentication app
│   ├── models.py             # ResetToken
│   ├── views.py
│   ├── templates/
│   └── urls.py
├── eCommerce/                 # eCommerce app
│   ├── models.py             # Store, Product, Review, Order, OrderItem
│   ├── views.py
│   ├── context_processors.py # Injects 'is_vendor' into every template
│   ├── templatetags/         # 'to_range' filter for stock-limited dropdowns
│   ├── migrations/           # includes a data migration that creates the
│   │                          # Vendors/Buyers groups and their permissions
│   ├── templates/
│   └── urls.py
├── manage.py
├── requirements.txt
├── .env.example
└── readme.md
```

## Troubleshooting

- **`ModuleNotFoundError: No module named 'django'`** — the virtual environment
  isn't activated, or `Django` is missing from `requirements.txt`.
- **`error: externally-managed-environment`** when running `pip install` — you're
  trying to install into the system Python. Use a virtual environment instead.
- **`Access denied for user 'root'@'localhost'` (error 1698)** — MariaDB's root
  account uses socket authentication. Log in with `sudo mysql -u root` instead
  of a password.
- **404 on `/accounts/login/`** — make sure `LOGIN_URL = 'grabsomore:login'` is
  set in `settings.py`; without it, Django's `@login_required` decorator falls
  back to a URL this project doesn't have.
- **`Product.MultipleObjectsReturned` when changing a price by name** — two
  products from different stores share the same name. Use the vendor panel
  (`/ecommerce/vendor/stores/<id>/products/`) to edit a specific product by ID
  instead of the name-based "Change Price" page.

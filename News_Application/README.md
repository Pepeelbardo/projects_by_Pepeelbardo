# Oxford News — Django News Application

A Django + Django REST Framework news platform where independent journalists and
publishers submit articles, editors review and approve them, and readers follow
the publishers and journalists they're interested in. Built as a capstone project.

## Features

- Custom user model with three roles (Reader, Editor, Journalist), each mapped
  automatically to a Django group with matching permissions (via signals, on
  `post_migrate` and on user save — no manual group setup needed).
- Publishers with associated editors and journalists.
- Article submission and editor approval workflow, with role-based access control.
- Newsletters: journalists create and edit their own; editors can edit or delete
  any newsletter.
- Follow system: readers follow individual journalists and/or publishers; the
  Following/Discover pages and the article detail page reflect this.
- On article approval, subscribers are notified by email and the article is
  logged to an internal REST endpoint (via Django signals).
- Full server-rendered website (no separate frontend framework, no external CSS
  — all styling is inline HTML `style` attributes): Home, Discover, Following,
  Article detail, My Articles / My Newsletters, Manage Articles / Manage
  Newsletters (editor), Pending Articles (editor approval queue), Newsletter
  list/detail, and an editable Account page (update email, change password).
- RESTful API (Django REST Framework) with JWT authentication and per-role
  permissions for articles.
- Automated test suite covering models, permissions, the API endpoints, and
  signal behavior (with mocking for email and the internal API call).
- Management command (`seed_articles`) to populate sample journalists,
  a publisher, and approved articles for quick manual testing.

## Tech Stack

- Python, Django 6.1, Django REST Framework
- MariaDB
- Simple JWT (`djangorestframework-simplejwt`)

## Prerequisites

- Python 3.12+ (required by Django 6.1)
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

This project lives inside the `News_Application` folder of a larger
repository. Clone the repository, then move into that folder:

```bash
git clone https://github.com/Pepeelbardo/projects_by_Pepeelbardo.git
cd projects_by_Pepeelbardo/News_Application
```

Everything below is run from inside this `News_Application` folder (the
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

Open `.env` and fill in each value. For `DJANGO_SECRET_KEY`, generate a fresh
random one — never reuse the example value or someone else's key. With the
virtual environment active:

```bash
python manage.py shell
```

Then, inside the shell:

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Copy the printed value into `DJANGO_SECRET_KEY` in your `.env`, then exit the
shell with `exit()`.

### 5. Set up the database

Log in to MariaDB as root (on a fresh Homebrew install, root has no password
and uses socket authentication, so use `sudo`):

```bash
sudo mysql -u root
```

Create the database and an application user (use the same values you put in
`.env`):

```sql
CREATE DATABASE oxfordnewsday CHARACTER SET utf8mb4;
CREATE USER 'oxfordnewsday_user'@'localhost' IDENTIFIED BY 'your-password';
GRANT ALL PRIVILEGES ON oxfordnewsday.* TO 'oxfordnewsday_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 6. Run migrations and start the server

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The Reader/Editor/Journalist groups and permissions are created automatically
the first time migrations run (via a signal, not a data migration) — no extra
setup needed.

### 7. (Optional) Load sample data

```bash
python manage.py seed_articles
```

Visit `http://127.0.0.1:8000/` to browse the site, or
`http://127.0.0.1:8000/admin/` for the Django admin panel with your superuser
account.

## Usage

- Visit `/` for the public homepage (search + featured article).
- Sign up as a Reader, Journalist, or Editor at `/accounts/signup/`.
- As a Reader: browse `/discover/` to search articles and follow authors or
  publishers, and check `/following/` for content from who you already follow.
- As a Journalist: create, edit, and delete your own articles and newsletters
  from the account menu (`My Articles`, `My Newsletters`); new articles stay
  pending until an Editor approves them.
- As an Editor: review submissions at `/editor/pending/`, manage all
  articles/newsletters from `/editor/manage/` and `/editor/newsletters/`, and
  create/manage Publishers (including which Editors and Journalists belong to
  each one) at `/editor/publishers/`.
- Everyone: manage your own email and password from `/account/`.

## API Endpoints

| Method | Endpoint                      | Access                      |
|--------|--------------------------------|------------------------------|
| POST   | `/api/token/`                  | Public — obtain a JWT        |
| GET    | `/api/articles/`               | Authenticated — approved only|
| GET    | `/api/articles/subscribed/`    | Authenticated (reader)       |
| GET    | `/api/articles/<id>/`          | Authenticated                |
| POST   | `/api/articles/`                | Journalist only              |
| PUT    | `/api/articles/<id>/`          | Journalist or Editor         |
| DELETE | `/api/articles/<id>/`          | Journalist or Editor         |
| POST   | `/api/approved/`               | Internal (signal-triggered)  |

Newsletters are only available through the website, not the REST API.

## Roles & Permissions

| Role       | Articles                                   | Newsletters                        | Publishers               |
|------------|---------------------------------------------|--------------------------------------|---------------------------|
| Reader     | View only; follow journalists/publishers    | View only                            | View only (via follow)   |
| Editor     | View, update, delete, approve (any)         | View, update, delete (any)           | Create, update, delete   |
| Journalist | Create, view, update, delete (own content)  | Create (own), view, update, delete (own) | None (assigned by Editor) |

## Publishers

Publishers are not self-service — there is no public registration form for
them, unlike Reader/Journalist/Editor accounts. An Editor creates a Publisher
from `/editor/publishers/` and assigns which existing Editors and Journalists
belong to it. A Journalist can only select a Publisher on their articles once
an Editor has added them to that Publisher's journalist list.

## Project structure

```
News_Application/
├── oxday/
│   ├── settings.py          # Project settings (reads DB/email config from .env)
│   ├── urls.py
│   └── wsgi.py
├── news/
│   ├── models.py             # User, Publisher, Article, Newsletter
│   ├── views.py               # Server-rendered pages (Home, Discover, dashboards...)
│   ├── api_views.py           # REST API viewsets
│   ├── serializers.py
│   ├── permissions.py         # ArticlePermission (role-based)
│   ├── forms.py
│   ├── signals.py             # Group sync + approval notifications
│   ├── management/commands/
│   │   └── seed_articles.py   # Sample data for manual testing
│   ├── migrations/
│   ├── templates/news/        # All HTML templates (inline styles, no CSS files)
│   ├── tests.py
│   ├── urls.py                # Server-rendered page routes
│   └── api_urls.py            # DRF router + API-only routes
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

## Running Tests

```bash
python manage.py test news
```

## Troubleshooting

- **`ModuleNotFoundError: No module named 'django'`** — the virtual environment
  isn't activated, or `Django` is missing from `requirements.txt`.
- **`error: externally-managed-environment`** when running `pip install` — you're
  trying to install into the system Python. Use a virtual environment instead.
- **`Access denied for user 'root'@'localhost'` (error 1698)** — MariaDB's root
  account uses socket authentication. Log in with `sudo mysql -u root` instead
  of a password.
- **`ImproperlyConfigured: Deprecated email settings are not allowed when
  MAILERS is defined`** — this project uses Django 6.1's `MAILERS` setting
  instead of the older `EMAIL_BACKEND`; don't add `EMAIL_BACKEND` back to
  `settings.py`.
- **A test user you created before switching databases no longer exists** — if
  you migrated from SQLite to MariaDB during development, all previously
  created users (including any manually-created superuser or test accounts)
  are gone; recreate them with `python manage.py createsuperuser` or the
  Django shell.
- **404 on `/accounts/login/`** — make sure `LOGIN_URL = 'login'` is set in
  `settings.py`; without it, Django's `@login_required` decorator falls back
  to a URL this project doesn't have.

## Author

Built by Pepeelbardo as part of the HyperionDev Software Engineering capstone.

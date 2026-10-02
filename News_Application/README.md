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
- Full server-rendered website styled with Bootstrap 5 (via CDN — no build step,
  no extra Python packages): Home, Discover, Following, Article detail, My
  Articles / My Newsletters, Manage Articles / Manage Newsletters (editor),
  Pending Articles (editor approval queue), Newsletter list/detail, and an
  editable Account page (update email, change password).
- RESTful API (Django REST Framework) with JWT authentication and per-role
  permissions for articles.
- Automated test suite covering models, permissions, the API endpoints, and
  signal behavior (with mocking for email and the internal API call).
- Management command (`seed_articles`) to populate sample journalists,
  a publisher, and approved articles for quick manual testing.
- Sphinx documentation for the `news` app, built into `docs/_build/html/`
  (open `docs/_build/html/index.html` in a browser).
- Dockerized: a `Dockerfile` and `docker-compose.yml` run the app and a MySQL
  database together with a single command — no local Python or database setup
  needed.

## Tech Stack

- Python, Django 6.1, Django REST Framework
- MySQL 8.4+ (MariaDB also works for local/venv development) — the Docker
  setup uses the official `mysql:8.4` image
- Simple JWT (`djangorestframework-simplejwt`)
- Bootstrap 5.3 (CDN)
- Docker & Docker Compose (optional, for containerized setup)

There are two ways to run this project: **with Docker** (fastest, no local
Python/MySQL install needed) or **with a virtual environment** (closer to a
normal local dev setup). Pick whichever you prefer — both are documented below.

## Secrets — read this before you do anything else

This repository does **not** contain a `.env` file, and it never should. `.env`
holds `DJANGO_SECRET_KEY` and the database credentials, and it's listed in
`.gitignore` on purpose so it can never be committed by accident.

Instead, the repo ships a `.env.example` with the variable names and dummy
placeholder values. To run the project — either with Docker or with a venv —
copy it and fill in real values yourself:

```bash
cp .env.example .env
```

- `DJANGO_SECRET_KEY` — generate your own; never reuse the placeholder or
  someone else's key (see "Getting started with a virtual environment", step
  4, for how to generate one).
- `DB_NAME`, `DB_USER`, `DB_PASSWORD` — choose your own values; you'll use the
  same ones when creating the database in step 5 (venv path) or they'll be
  passed straight into the MySQL container (Docker path).
- `DB_HOST` / `DB_PORT` — `localhost` / `3306` for the venv path; the Docker
  path overrides `DB_HOST` to `db` automatically via `docker-compose.yml`, so
  you don't need to change it.

**If you're reviewing this submission:** rather than editing `.env.example` in
place, you can create your own `.env` from it as shown above — it's already
gitignored, so it's safe to fill in and won't end up in a commit. If you'd
rather not leave even a local `.env` lying around after the review, delete it
once you're done (`rm .env`); the project won't run without one, by design.

## Running with Docker

This is the quickest way to get the whole stack (Django + MySQL) running on
any machine with Docker installed, including the Docker Playground.

### 1. Clone the repository

```bash
git clone https://github.com/Pepeelbardo/news_app_capstone.git
cd news_app_capstone
```

### 2. Create your `.env` file

```bash
cp .env.example .env
```

Fill in `DJANGO_SECRET_KEY`, `DB_NAME`, `DB_USER`, and `DB_PASSWORD` with your
own values (see "Secrets" above). You can leave `DB_HOST` and `DB_PORT` as-is —
`docker-compose.yml` points the app at the `db` container automatically.

### 3. Build and start the containers

```bash
docker compose up --build
```

This builds the Django image, starts a MySQL 8.4 container, waits for MySQL to
report healthy, then runs migrations and starts the dev server automatically.
The Reader/Editor/Journalist groups are created on first migration — no extra
setup needed.

### 4. Create a superuser (optional, in a second terminal)

```bash
docker compose exec web python manage.py createsuperuser
```

### 5. (Optional) Load sample data

```bash
docker compose exec web python manage.py seed_articles
```

Visit `http://localhost:8000/` to browse the site, or
`http://localhost:8000/admin/` for the Django admin panel.

Database data persists in a named Docker volume (`mysql_data`) across
restarts. To stop the containers: `docker compose down` (keeps the data) or
`docker compose down -v` (also wipes the database volume, e.g. if you need a
fresh start).

## Getting started with a virtual environment

These steps assume you don't have this project on your machine yet — just a
link to the GitHub repository.

### 1. Clone the repository and enter the project folder

```bash
git clone https://github.com/Pepeelbardo/news_app_capstone.git
cd news_app_capstone
```

Everything below is run from inside this folder (the one that contains
`manage.py`).

### 2. Create and activate a virtual environment

```bash
python3 -m venv Newsenv
source Newsenv/bin/activate
```

(`Newsenv` is the name already listed in `.gitignore`; you can use a
different name, just make sure it's not accidentally committed.)

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

Copy the example file and fill in real values (see "Secrets" above for what
each one means):

```bash
cp .env.example .env
```

For `DJANGO_SECRET_KEY`, generate a fresh random one — never reuse the
example value or someone else's key. With the virtual environment active:

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

Log in to MariaDB/MySQL as root (on a fresh Homebrew MariaDB install, root has
no password and uses socket authentication, so use `sudo`):

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
  pending until an Editor approves.
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
news_app_capstone/
├── oxday/
│   ├── settings.py          # Project settings (reads DB/email config from .env)
│   ├── urls.py
│   └── wsgi.py
├── news/
│   ├── models.py            # User, Publisher, Article, Newsletter
│   ├── views.py               # Server-rendered pages (Home, Discover, dashboards...)
│   ├── api_views.py           # REST API viewsets
│   ├── serializers.py
│   ├── permissions.py         # ArticlePermission (role-based)
│   ├── forms.py
│   ├── signals.py             # Group sync + approval notifications
│   ├── management/commands/
│   │   └── seed_articles.py   # Sample data for manual testing
│   ├── migrations/
│   ├── templates/news/        # All HTML templates (Bootstrap 5 via CDN)
│   ├── tests.py
│   ├── urls.py                # Server-rendered page routes
│   └── api_urls.py            # DRF router + API-only routes
├── docs/                      # Sphinx documentation sources + built HTML
│   └── _build/html/index.html # Open this in a browser to read the docs
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
└── README.md
```

## Running Tests

```bash
python manage.py test news
```

(Or, with Docker running: `docker compose exec web python manage.py test news`.)

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
- **Docker: `NotSupportedError: MySQL 8.4 or later is required`** — this means
  an old MySQL data volume from a previous run is still around. Run
  `docker compose down -v` to remove it, then `docker compose up --build`
  again to start fresh with MySQL 8.4.
- **Docker: `web` container keeps restarting** — check its logs with
  `docker compose logs web`; the most common cause is a missing or incomplete
  `.env` file (see "Secrets" above).

## Author

Built by Pepeelbardo as part of the HyperionDev Software Engineering capstone.

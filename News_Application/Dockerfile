FROM python:3.12-slim

# Django 6.1 requires Python 3.12+, and one of our views (news/api_views.py)
# uses a multi-line f-string that only parses on Python 3.12+ (PEP 701).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System libraries needed to build mysqlclient from source.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        default-libmysqlclient-dev \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Apply migrations, then start the dev server bound to all interfaces so it's
# reachable from outside the container.
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8000"]

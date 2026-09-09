"""Register your models here."""
from django.contrib import admin

from .models import Article, Newsletter, Publisher, User

admin.site.register(User)
admin.site.register(Publisher)
admin.site.register(Article)
admin.site.register(Newsletter)

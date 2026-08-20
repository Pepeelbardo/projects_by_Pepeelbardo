from django.contrib import admin

from .models import Order, OrderItem, Product, Review, Store

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Product)
admin.site.register(Review)
admin.site.register(Store)

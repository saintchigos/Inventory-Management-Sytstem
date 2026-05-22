from django.contrib import admin
from .models import Category, Location, Item, StockMovement


admin.site.register(Category)
admin.site.register(Location)
admin.site.register(Item)
admin.site.register(StockMovement)
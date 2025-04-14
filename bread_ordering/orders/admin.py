from django.contrib import admin
from .models import Bread, Order

admin.site.register(Order)

@admin.register(Bread)
class BreadAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock')

from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['Product_name', 'quantity', 'unit_price', 'image']
    search_fields = ['Product_name']
# Register your models here.

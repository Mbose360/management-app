from django.contrib import admin

from .models import ReservationProduct,RequestedProduct,Reservation

# Register your models here.
class ReservationProductInline(admin.TabularInline):
    model = ReservationProduct
    extra = 1

class RequestedProductInline(admin.TabularInline):
    model = RequestedProduct
    extra = 1

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display= ['client', 'reservation_date', 'total_price', 'status']
    list_filter = ['reservation_date', 'status']
    search_fields = ['client__name']
    inlines = [ReservationProductInline, RequestedProductInline]

@admin.register(RequestedProduct)
class RequestedProductAdmin(admin.ModelAdmin):
    list_display = ['reservation', 'name', 'requested_quantity']
    search_fields = ['name']
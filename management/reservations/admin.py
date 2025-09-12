from django.contrib import admin
from .models import Reservation, ReservationProduct, RequestedProduct
import logging

logger = logging.getLogger(__name__)

class ReservationProductInline(admin.TabularInline):
    model = ReservationProduct
    extra = 1

class RequestedProductInline(admin.TabularInline):
    model = RequestedProduct
    extra = 1

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['client', 'reservation_date', 'total_price', 'status']
    list_filter = ['reservation_date', 'status']
    search_fields = ['client__name']
    inlines = [ReservationProductInline, RequestedProductInline]

    def save_model(self, request, obj, form, change):
        logger.debug(f"Saving Reservation {obj.id or 'new'} in admin")
        super().save_model(request, obj, form, change)
        obj.total_price = obj.calculate_total_price()
        obj.status = 'partially_fulfilled' if obj.requestedproduct_set.exists() else 'confirmed'
        obj.save(update_fields=['total_price', 'status'])
        logger.debug(f"Updated Reservation {obj.id}: total_price={obj.total_price}, status={obj.status}")

@admin.register(RequestedProduct)
class RequestedProductAdmin(admin.ModelAdmin):
    list_display = ['reservation', 'name', 'requested_quantity']
    search_fields = ['name']
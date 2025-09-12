from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from inventory.models import Product
from clients.models import Client


class Reservation(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    reservation_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('partially_fulfilled', 'Partially Fulfilled'), ('confirmed', 'Confirmed')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reservation for {self.client} on {self.reservation_date}"


class ReservationProduct(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='items' )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    
    @property
    def item_subtotal(self):
        return self.product.unit_price * self.quantity


class RequestedProduct(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    requested_quantity = models.PositiveIntegerField()
    suggested_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Requested {self.name} for {self.reservation}"


from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from inventory.models import Product
from clients.models import Client

# Create your models here.
class Reservation(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    reservation_date = models.DateField()
    total_price = models.DecimalField(max_digits=10,decimal_places=2, default=0.00)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'),
        ('partially_fulfilled', 'Partially Fulfilled'), ('confirmed', 'Confirmed')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reservation for{self.client} on {self.reservation_date}"

class ReservationProduct(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    class Meta:
        unique_together = ('reservation', 'product')



class RequestedProduct (models.Model):
    Reservation = models.ForeignKey(Reservation, on_delete= models.CASCADE)
    name = models.CharField(max_length=100)
    requested_quanity = models.PositiveIntegerField()
    suggested_price = models.DecimalField( max_digits=10, decimal_places=2, null = True , blank=True)

def __str__(self):
        return f"Requested {self.name} for {self.reservation}"

@receiver(post_save, sender=Reservation)
def update_reservation_logic(sender, instance, created, **kwargs):
    if created:
        same_day_reservations = Reservation.objects.filter(reservation_date=instance.reservation_date).count()
        if same_day_reservations >= 2:
            # Reduce quantity for existing products
            for rp in instance.reservationproduct_set.all():
                if rp.quantity > rp.product.quantity:
                    excess = rp.quantity - rp.product.quantity
                    RequestedProduct.objects.create(
                        reservation=instance,
                        name=rp.product.product_name,
                        requested_quantity=excess,
                        suggested_price=rp.product.unit_price
                    )
                    rp.quantity = rp.product.quantity  # Use available quantity
                    rp.product.quantity = 0
                else:
                    rp.product.quantity -= rp.quantity
                rp.product.save()
        else:
            # Mark as requested if insufficient
            for rp in instance.reservationproduct_set.all():
                if rp.quantity > rp.product.quantity:
                    RequestedProduct.objects.create(
                        reservation=instance,
                        name=rp.product.product_name,
                        requested_quantity=rp.quantity,
                        suggested_price=rp.product.unit_price
                    )
                    rp.quantity = 0
                    rp.save()

        # Calculate total price
        total = sum(
            rp.product.unit_price * rp.quantity
            for rp in instance.reservationproduct_set.all()
            if rp.product.unit_price and rp.quantity > 0
        )
        for req in instance.requestedproduct_set.all():
            if req.suggested_price:
                total += req.suggested_price * req.requested_quantity
        instance.total_price = total
        if instance.requestedproduct_set.exists():
            instance.status = 'partially_fulfilled'
        instance.save()

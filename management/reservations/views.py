from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db import transaction
from .models import Reservation, ReservationProduct, RequestedProduct, Product
from .serializers import RequestedProductSerializer, ReservationSerializer,RequestedProduct2Serializer

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            reservation = serializer.save()
            return Response(
                {
                    "id": reservation.id,
                    "client": reservation.client_id,
                    "reservation_date": reservation.reservation_date,
                    "status": reservation.status,
                    "items": [
                        {
                            "product_name": item.product.Product_name,
                            "unit_price": item.product.unit_price,
                            "quantity": item.quantity
                        } for item in reservation.items.all()
                    ],
                    "requested_products": [
                        {
                            "name": rp.name,
                            "requested_quantity": rp.requested_quantity,
                            "suggested_price": rp.suggested_price
                        } for rp in reservation.requestedproduct_set.all()
                    ],
                    "total_price": reservation.total_price
                },
                status=status.HTTP_201_CREATED
            )

class RequestedProductViewSet(viewsets.ModelViewSet):
    queryset=RequestedProduct.objects.all()
    serializer_class=RequestedProductSerializer

   




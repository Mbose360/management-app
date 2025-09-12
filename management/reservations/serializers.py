from rest_framework import serializers

from clients.serializers import ClientSerializer
from inventory.serializers import ProductSerializer
from .models import Reservation, ReservationProduct, RequestedProduct
from clients.models import Client
from inventory.models import Product


class ReservationProductSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.Product_name')
    unit_pric = serializers.DecimalField(max_digits=10, decimal_places=2,source='product.unit_price')
    class Meta:
        
        model = ReservationProduct
        fields = ['product_name','unit_pric', 'quantity']




class ReservationSerializer(serializers.ModelSerializer):
    items = ReservationProductSerializer (many = True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, obj):
        order_items = obj.items.all()
        return sum(order_item.item_subtotal for order_item in order_items) 
    
    class Meta:
        
        model = Reservation
        fields = ['id', 'client', 'reservation_date', 'status', 'items','total_price',]
        read_only = ['created_at',]
    
    def validate(self, data):
        if not self.context['request'].data.get('products'):
            raise serializers.ValidationError("At least one product is required.")
        return data

class RequestedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestedProduct
        fields = ['name', 'requested_quantity', 'suggested_price']
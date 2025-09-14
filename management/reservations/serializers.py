from rest_framework import serializers
from clients.serializers import ClientSerializer
from inventory.serializers import ProductSerializer
from .models import Reservation, ReservationProduct, RequestedProduct
from clients.models import Client
from inventory.models import Product

class ReservationProductSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.Product_name', read_only=True)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, source='product.unit_price', read_only=True) # Fixed typo: unit_pric -> unit_price
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True)
  
    class Meta:
        model = ReservationProduct
        fields = ['product', 'quantity','unit_price','product_name']
        read_only_fields = ['unit_price','product_name']

    def validate(self, data):
        product = data.get('product')
        quantity = data.get('quantity')
        if quantity > product.quantity:
            raise serializers.ValidationError(f"Not enough stock for {product.Product_name}.")
        if product.unit_price is None:
            raise serializers.ValidationError(f"Unit price missing for {product.Product_name}.")
        return data

class RequestedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestedProduct
        fields = ['name', 'requested_quantity', 'suggested_price']

    def validate(self, data):
        if data.get('suggested_price') is None:
            raise serializers.ValidationError("Suggested price is required for requested products.")
        return data

class ReservationSerializer(serializers.ModelSerializer):
    items = ReservationProductSerializer(many=True, required=False)
    requested_products = RequestedProductSerializer(many=True, required=False)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Reservation
        fields = ['id', 'client', 'reservation_date', 'status', 'items', 'requested_products', 'total_price', 'created_at']
        read_only_fields = ['total_price', 'created_at']

    def validate(self, data):
        products = self.context['request'].data.get('items', [])
        requested_products = self.context['request'].data.get('requested_products', [])
        if not products and not requested_products:
            raise serializers.ValidationError("At least one product or requested product is required.")
        return data

    def create(self, validated_data):
        products_data = validated_data.pop('items', [])
        requested_products_data = validated_data.pop('requested_products', [])
        reservation = Reservation.objects.create(**validated_data)
        
        for product_data in products_data:
            ReservationProduct.objects.create(reservation=reservation, **product_data)
        
        for requested_product_data in requested_products_data:
            RequestedProduct.objects.create(reservation=reservation, **requested_product_data)
        
        # Calculate and save total price
        total_price = sum(item.item_subtotal for item in reservation.items.all())
        total_price += sum(
            rp.requested_quantity * rp.suggested_price
            for rp in reservation.requestedproduct_set.all()
            if rp.suggested_price is not None
        )
        reservation.total_price = total_price
        reservation.save()
        return reservation
    


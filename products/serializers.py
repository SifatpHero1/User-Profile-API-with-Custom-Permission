from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)  # ← read_only!

    class Meta:
        model = Product
        fields = ('id', 'owner', 'name', 'description', 'price', 'stock', 'image', 'created_at', 'updated_at')
        read_only_fields = ('id', 'owner', 'created_at', 'updated_at')
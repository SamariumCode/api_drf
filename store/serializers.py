from decimal import Decimal
from rest_framework import serializers

from store.models import Category, Product


class CategorySerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=500)


class ProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    unit_price = serializers.DecimalField(
        max_digits=6, decimal_places=2)

    unit_price_after_tax = serializers.SerializerMethodField(
        method_name='calculate_tax')
    inventory = serializers.IntegerField()

    # category = serializers.PrimaryKeyRelatedField(
    #     queryset=Category.objects.all()
    # )

    # category = CategorySerializer()
    category = serializers.HyperlinkedRelatedField(

        queryset=Category.objects.all(),
        view_name='category-detail',
    )

    # Custom Method Field

    def calculate_tax(self, product: Product):
        return round(product.unit_price * Decimal(1.09), 2)

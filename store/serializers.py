from decimal import Decimal
from django.utils.text import slugify
from rest_framework import serializers

from store.models import Category, Product, Comment, Order, Cart, CartItem


class CategorySerializer(serializers.ModelSerializer):
    # count_category = serializers.SerializerMethodField()

    count_category = serializers.IntegerField(
        source='products.count', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'title', 'description', 'count_category']

    # def get_count_category(self, category: Category):
    #     return category.products.count()


class ProductSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=255, source='name')
    price = serializers.DecimalField(
        max_digits=6, decimal_places=2, source='unit_price')

    unit_price_after_tax = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'price',
                  'category', 'unit_price_after_tax', 'inventory', 'slug', 'description']
        read_only_fields = ['slug']  # Make slug read-only

    def get_unit_price_after_tax(self, product: Product):
        return round(product.unit_price * Decimal(1.09), 2)

    def validate(self, data):
        if len(data['name']) < 6:
            raise serializers.ValidationError(
                'Product Title length shod be at least sex')

        return data

    def create(self, validated_data):
        # Retrieve the value of the 'name' field from validated_data
        name = validated_data.get('name')

        # Generate a slug (URL-friendly version) from her own name
        validated_data['slug'] = slugify(name)

        # Call the parent class's 'create' method to save the object
        return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'name', 'body']

    def create(self, validated_data):
        product_id = self.context['product_pk']
        return Comment.objects.create(product_id=product_id, **validated_data)


class CartProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'unit_price']


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class AddCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']

    def create(self, validated_data):
        cart_id = self.context['cart_pk']

        product = validated_data.get('product')
        quantity = validated_data.get('quantity')

        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product.id)
            cart_item.quantity += quantity
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(cart_id=cart_id, **validated_data)

        self.instance = cart_item

        return cart_item


class CartItemSerializer(serializers.ModelSerializer):
    product = CartProductSerializer(read_only=True)

    item_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'item_total']

    def get_item_total(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.product.unit_price


class CartSerializer(serializers.ModelSerializer):
    # id = serializers.UUIDField(source='pk', read_only=True)
    items = CartItemSerializer(many=True, read_only=True)

    unit_price_total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'unit_price_total']
        read_only_fields = ['id']

    def get_unit_price_total(self, cart: Cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])

from django.db.models import Count, Prefetch
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet, GenericViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny, DjangoModelPermissions

from .filters import ProductFilter
from .models import Category, Order, Product, Comment, Cart, CartItem, Customer, OrderItem
from .paginations import DefaultPagination
from .serializers import ProductSerializer, CategorySerializer, CommentSerializer, CartSerializer, CartItemSerializer, \
    AddCartItemSerializer, UpdateCartItemSerializer, CustomerSerializer, OrderSerializer, OredrItemSerializer, OrderForAdminSerializer, OrderCreateSerializer
from .permissions import IsAdminOrReadOnly, SendPrivateEmail, CustomDjangoModelPermissions


class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer

    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    # filterset_fields = ['category_id', 'category__title', 'inventory']
    filterset_class = ProductFilter
    ordering_fields = ['name', 'unit_price']
    search_fields = ['name']

    pagination_class = DefaultPagination
    permission_classes = [CustomDjangoModelPermissions]

    queryset = Product.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, pk):
        product = get_object_or_404(
            Product.objects.select_related('category'), pk=pk)
        if product.order_items.count() > 0:
            return Response({'error': 'There is some order items including this product please remove the first'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

        product = get_object_or_404(
            Product.objects.select_related('category'), pk=pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryViewSet(ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.filter().prefetch_related('products').all()
    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, pk):
        category = get_object_or_404(
            Category.objects.prefetch_related('products'), pk=pk)
        if category.products.count() > 0:
            return Response({'error': 'There is some products relating  this category. please remove the first'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        product_pk = self.kwargs['product_pk']

        return Comment.objects.filter(product_id=product_pk).all()

    def get_serializer_context(self):
        return {'product_pk': self.kwargs['product_pk']}


class CartViewSet(CreateModelMixin,
                  RetrieveModelMixin,
                  DestroyModelMixin,
                  GenericViewSet):
    serializer_class = CartSerializer
    queryset = Cart.objects.prefetch_related('items__product').all()
    lookup_value_regex = '[0-9a-fA-F]{8}\-?[0-9a-fA-F]{4}\-?[0-9a-fA-F]{4}\-?[0-9a-fA-F]{4}\-?[0-9a-fA-F]{12}'


class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        cart_pk = self.kwargs['cart_pk']
        return CartItem.objects.select_related('product').filter(cart_id=cart_pk).all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        return {'cart_pk': self.kwargs['cart_pk']}


class CustomerViewSet(ModelViewSet):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['get', 'put'], permission_classes=[IsAuthenticated])
    def me(self, request):

        user_id = request.user.id
        customer = Customer.objects.get(user_id=user_id)

        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)

        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    @action(detail=True, permission_classes=[SendPrivateEmail])
    def send_private_email(self, request, pk):
        return Response(f'sending email for customer {pk}')


class OrderViewSet(ModelViewSet):
    # serializer_class = OrderSerializer

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Order.objects.prefetch_related(

            Prefetch(

                'items',
                queryset=OrderItem.objects.select_related(
                    'product'),


            )

        ).select_related('customer__user').all()

        user = self.request.user

        if user.is_staff:
            return queryset
        return queryset.filter(customer__user_id=user.id)

    def get_serializer_class(self):

        if self.request.method == 'POST':
            return OrderCreateSerializer

        if self.request.user.is_staff:
            return OrderForAdminSerializer
        return OrderSerializer

    def get_serializer_context(self):
        return {'user_id': self.request.user.id}

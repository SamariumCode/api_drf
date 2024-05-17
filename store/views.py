from django.db.models import Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .models import Category, Product, Comment
from .serializers import ProductSerializer, CategorySerializer, CommentSerializer
from .filters import ProductFilter


class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer

    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    # filterset_fields = ['category_id', 'category__title', 'inventory']
    filterset_class = ProductFilter
    ordering_fields = ['name', 'unit_price']
    search_fields = ['name']

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

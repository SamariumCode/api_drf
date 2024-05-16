from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Product
from .serializers import ProductSerializer, CategorySerializer


class ProductList(ListCreateAPIView):

    serializer_class = ProductSerializer

    # def get_serializer_class(self):
    #     return ProductSerializer

    queryset = Product.objects.order_by('id').select_related(
        'category').prefetch_related('discounts').all()

    # def get_queryset(self):
    #     return Product.objects.filter(name__istartswith='S').select_related('category').prefetch_related('discounts').all()

    def get_serializer_context(self):
        return {'request': self.request}


class ProductDetail(RetrieveUpdateDestroyAPIView):

    serializer_class = ProductSerializer

    queryset = Product.objects.select_related('category').all()

    # lookup_field = 'id'

    def delete(self, request, pk):
        product = get_object_or_404(
            Product.objects.select_related('category'), pk=pk)
        if product.order_items.count() > 0:
            return Response({'error': 'There is some order items including this product please remove the first'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        product = get_object_or_404(
            Product.objects.select_related('category'), pk=pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryList(ListCreateAPIView):
    serializer_class = CategorySerializer
    queryset = queryset = Category.objects.filter().prefetch_related('products').all()


class CategoryDetail(RetrieveUpdateDestroyAPIView):

    serializer_class = CategorySerializer

    queryset = Category.objects.prefetch_related('products').all()

    def delete(self, request, pk):
        category = get_object_or_404(
            Category.objects.prefetch_related('products'), pk=pk)
        if category.products.count() > 0:
            return Response({'error': 'There is some products relating  this category. please remove the first'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

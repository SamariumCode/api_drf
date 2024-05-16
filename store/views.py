from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import ListCreateAPIView
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


class ProductDetail(APIView):
    def get(self, request, pk):
        product = get_object_or_404(
            Product.objects.select_related('category'), pk=pk)
        serializer = ProductSerializer(
            product, context={'request': request})  # convert to json
        return Response(serializer.data)

    def put(self, request, pk):
        product = get_object_or_404(
            Product.objects.select_related('category'), pk=pk)
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

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


class CategoryDetail(APIView):
    def get(self, request, pk):
        category = get_object_or_404(Category.objects.filter().annotate(
            products_count=Count('products')), pk=pk)
        serializer = CategorySerializer(category)  # convert to json
        return Response(serializer.data)

    def put(self, request, pk):
        category = get_object_or_404(Category.objects.filter().annotate(
            products_count=Count('products')), pk=pk)
        serializer = CategorySerializer(category, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        category = get_object_or_404(Category.objects.filter().annotate(
            products_count=Count('products')), pk=pk)
        if category.products_count > 0:
            return Response({'error': 'There is some products relating  this category. please remove the first'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

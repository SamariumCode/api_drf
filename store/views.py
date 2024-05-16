from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Product
from .serializers import ProductSerializer, CategorySerializer


class ProductList(APIView):
    def get(self, request):
        queryset = Product.objects.filter(
            name__istartswith='S').select_related('category').prefetch_related('discounts')
        serializer = ProductSerializer(
            queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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


class CategoryList(APIView):
    def get(self, request):
        queryset = Category.objects.filter().annotate(
            products_count=Count('products')).all()

        serializer = CategorySerializer(
            queryset, many=True, context={'request': request})

        return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


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

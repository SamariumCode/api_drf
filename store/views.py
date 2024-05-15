from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count

from .models import Category, Product
from .serializers import ProductSerializer, CategorySerializer


@api_view(['GET', 'POST'])
def product_list(request):
    if request.method == 'GET':
        queryset = Product.objects.filter(
            name__istartswith='S').select_related('category').prefetch_related('discounts')

        serializer = ProductSerializer(
            queryset, many=True, context={'request': request})

        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
def product_detail(request, pk):

    product = get_object_or_404(
        Product.objects.select_related('category'), pk=pk)

    if request.method == 'GET':
        serializer = ProductSerializer(
            product, context={'request': request})  # convert to json
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    elif request.method == 'DELETE':
        if product.order_items.count() > 0:
            return Response({'error': 'There is some order items including this product please remove the first'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        product = get_object_or_404(
            Product.objects.select_related('category'), pk=pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def category_list(request):
    if request.method == 'GET':
        queryset = Category.objects.filter().annotate(
            products_count=Count('products')).all()

        serializer = CategorySerializer(
            queryset, many=True, context={'request': request})

        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'PUT', 'DELETE'])
def category_detail(request, pk):

    category = get_object_or_404(Category.objects.filter().annotate(
        products_count=Count('products')), pk=pk)

    if request.method == 'GET':
        serializer = CategorySerializer(category)  # convert to json
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = CategorySerializer(category, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    elif request.method == 'DELETE':
        if Category.objects.filter().select_related('products').count() > 0:
            return Response({'error': 'There is some products relating  this category. please remove the first'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        category = get_object_or_404(
            Category.objects.prefetch_related('products'), pk=pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

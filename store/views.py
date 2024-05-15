from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

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
        return Response('Everything is OK')


@api_view()
def product_detail(request, pk):

    product = get_object_or_404(
        Product.objects.select_related('category'), pk=pk)

    serializer = ProductSerializer(
        product, context={'request': request})  # convert to json
    return Response(serializer.data)


@api_view()
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)

    serializer = CategorySerializer(category)

    return Response(serializer.data)

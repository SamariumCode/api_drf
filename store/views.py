from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Product
from .serializers import ProductSerializer


@api_view()
def product_list(request):
    return Response('Hi')


@api_view()
def product_detail(request, pk):

    product = get_object_or_404(Product, pk=pk)

    # try:
    #     product = Product.objects.get(pk=pk)
    # except Product.DoesNotExist:
    #     return Response(status=status.HTTP_404_NOT_FOUND)  # Not Found

    serializer = ProductSerializer(product)  # convert to json
    return Response(serializer.data)

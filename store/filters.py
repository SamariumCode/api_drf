from django_filters.rest_framework import FilterSet

from store.models import Product


class ProductFilter(FilterSet):
    class Meta:
        model = Product
        fields = {
            'inventory': ['lt', 'gt'],
            # 'category__title': ['icontains', 'istartswith'],
            'name': ['startswith'],
        }

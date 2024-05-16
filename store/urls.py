from django.urls import path, include
from rest_framework.routers import SimpleRouter, DefaultRouter

from . import views


router = DefaultRouter()
router.register('products', views.ProductViewSet,
                basename='product')  # product_list, product_detial
router.register('categories', views.CategoryViewSet,
                basename='category')  # category_list, category_detial

urlpatterns = router.urls


# urlpatterns = [
#     path('', include(router.urls))
# ]

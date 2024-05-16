from django.urls import path, include
from rest_framework_nested import routers

from . import views


router = routers.DefaultRouter()
router.register('products', views.ProductViewSet,
                basename='product')  # product_list, product_detial
router.register('categories', views.CategoryViewSet,
                basename='category')  # category_list, category_detial


products_router = routers.NestedDefaultRouter(
    router, 'products', lookup='product')

products_router.register(
    'comments', views.CommentViewSet, basename='product-comment')


urlpatterns = router.urls + products_router.urls

# mywebsite.com/products/553:product_pk/comments/8:pk  Nested Routing


# urlpatterns = [
#     path('', include(router.urls))
# ]

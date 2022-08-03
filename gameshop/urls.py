"""gameshop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from shop_api.views import ProductViewSet, CommentViewSet, CategoryViewSet, OrderViewSet, OrderItemViewSet, \
    WishListViewSet, ProductMediaViewSet
from rest_framework_nested import routers

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'products', ProductViewSet, basename='Product')
router.register(r'categories', CategoryViewSet, basename='Category')
router.register(r'orders', OrderViewSet, basename='Orders')
router.register(r'wishlist', WishListViewSet, basename='WishList')
comments_router = routers.NestedDefaultRouter(
    router,
    r'products',
    lookup='product'
)
comments_router.register(r'comments',
                         CommentViewSet,
                         basename='comments'
                         )
order_item_router = routers.NestedDefaultRouter(
    router,
    r'orders',
    lookup='order'
)
order_item_router.register(r'order_items',
                           OrderItemViewSet,
                           basename='order_items'
                           )
product_media_router = routers.NestedDefaultRouter(
    router,
    r'products',
    lookup='product'
)
product_media_router.register(
    r'media',
    ProductMediaViewSet,
    basename='media'
)
urlpatterns = [
    path('', include(router.urls)),
    path('', include(order_item_router.urls)),
    path('', include(comments_router.urls)),
    path('', include(product_media_router.urls)),
    path('auth/', include('auth.urls')),
]

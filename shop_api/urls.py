from django.urls import path
from .views import LatestProductsViewSet

urlpatterns = [
    path('latest_products/', LatestProductsViewSet.as_view(), name='latest'),
]

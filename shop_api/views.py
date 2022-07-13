from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .serializers import ProductSerializer
from .models import Product
from rest_framework.permissions import IsAdminUser, SAFE_METHODS, BasePermission


# Create your views here.
class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class ProductViewSet(ModelViewSet):
    permission_classes = [IsAdminUser | ReadOnly]
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

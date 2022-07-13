from django.shortcuts import render
from rest_framework import serializers
from rest_framework.viewsets import ModelViewSet
from .serializers import ProductSerializer, CommentSerializer, UserSerializer
from .models import Product, Comment
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser, SAFE_METHODS, BasePermission


# Create your views here.
class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class ProductViewSet(ModelViewSet):
    permission_classes = [IsAdminUser | ReadOnly]
    serializer_class = ProductSerializer
    queryset = Product.objects.all()


class CommentViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

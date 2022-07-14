from rest_framework.viewsets import ModelViewSet
from .serializers import ProductShowSerializer, ProductCreateSerializer, CommentSerializer, CategorySerializer
from .models import Product, Comment, Category
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser, SAFE_METHODS, BasePermission


# Create your views here.
class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class ProductDualViewSet(ModelViewSet):
    permission_classes = [IsAdminUser | ReadOnly]
    queryset = Product.objects.all()
    serializer_classes = {
        'create': ProductCreateSerializer,
        'update': ProductCreateSerializer,
        'partial_update': ProductCreateSerializer,
        'destroy': ProductCreateSerializer
    }
    default_serializer_class = ProductShowSerializer

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)


class CommentViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()


class CategoryViewSet(ModelViewSet):
    permission_classes = [IsAdminUser | ReadOnly]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

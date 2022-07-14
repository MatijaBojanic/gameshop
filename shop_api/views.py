from rest_framework.viewsets import ModelViewSet
from .serializers import ProductShowSerializer, ProductCreateSerializer, CommentSerializer, CategoryShowSerializer, \
    CategoryCreateSerializer, OrderSerializer, OrderItemSerializer
from .models import Product, Comment, Category, Order, OrderItem
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser, SAFE_METHODS, \
    BasePermission


# Create your views here.
class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class ProductViewSet(ModelViewSet):
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
    queryset = Category.objects.all()

    serializer_classes = {
        'create': CategoryCreateSerializer,
        'update': CategoryCreateSerializer,
        'partial_update': CategoryCreateSerializer,
        'destroy': CategoryCreateSerializer
    }
    default_serializer_class = CategoryShowSerializer

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)


class OrderViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer
    queryset = Order.objects.all()


class OrderItemViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer
    queryset = OrderItem.objects.all()

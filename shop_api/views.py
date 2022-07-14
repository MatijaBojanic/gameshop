from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.viewsets import ModelViewSet
from .serializers import ProductShowSerializer, ProductCreateSerializer, CommentSerializer, CategoryShowSerializer, \
    CategoryCreateSerializer, OrderSerializer, OrderItemSerializer, WishListShowSerializer, WishListCreateSerializer
from .models import Product, Comment, Category, Order, OrderItem, WishList
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

    def get_queryset(self, *args, **kwargs):
        product_id = self.kwargs.get("product_pk")
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise NotFound('A product with this id does not exist')
        return self.queryset.filter(product=product)

    def perform_create(self, serializer):
        serializer.save(product=Product.objects.get(id=self.kwargs.get("product_pk")),
                        user=self.request.user
                        )


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

    def get_queryset(self, *args, **kwargs):
        product_id = self.kwargs.get("product_pk")
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise NotFound('A product with this id does not exist')
        return self.queryset.filter(product=product)

    def perform_create(self, serializer):
        serializer.save(product=Product.objects.get(id=self.kwargs.get("product_pk")))


class OrderViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderItemViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderItemSerializer
    queryset = OrderItem.objects.all()

    def get_queryset(self, *args, **kwargs):
        order_id = self.kwargs.get("order_pk")
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise NotFound('An order with this id does not exist')
        return self.queryset.filter(order=order)

    def perform_create(self, serializer):
        serializer.save(order=Order.objects.get(id=self.kwargs.get("order_pk")))


class WishListViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_classes = {
        'create': WishListCreateSerializer,
        'update': WishListCreateSerializer,
        'partial_update': WishListCreateSerializer,
        'destroy': WishListCreateSerializer
    }
    default_serializer_class = WishListShowSerializer

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    def get_queryset(self):
        if self.request.user.is_staff:
            return WishList.objects.all()
        return WishList.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        try:
            if WishList.objects.get(user=self.request.user):
                raise ValidationError("Wishlist for this user already exists")
        except WishList.DoesNotExist:
            serializer.save(user=self.request.user)


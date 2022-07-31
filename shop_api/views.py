from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from .serializers import ProductShowSerializer, ProductDetailsSerializer, ProductCreateSerializer, CommentSerializer, \
    CategoryShowSerializer, \
    CategoryCreateSerializer, OrderSerializer, OrderItemSerializer, WishListShowSerializer, WishListCreateSerializer, \
    ProductMediaSerializer
from .models import Product, Comment, Category, Order, OrderItem, WishList, ProductMedia
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser, SAFE_METHODS, \
    BasePermission
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, mixins
from django.utils import timezone


# Create your views here.
class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class ProductMediaViewSet(ModelViewSet):
    permission_classes = [IsAdminUser | ReadOnly]
    serializer_class = ProductMediaSerializer
    queryset = ProductMedia.objects.all()

    def get_queryset(self, *args, **kwargs):
        product_id = self.kwargs.get("product_pk")
        print(product_id)
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise NotFound('A product with this id does not exist')
        return self.queryset.filter(product=product)

    def perform_create(self, serializer):
        serializer.save(product=Product.objects.get(id=self.kwargs.get("product_pk")))


class ProductViewSet(ModelViewSet):
    permission_classes = [IsAdminUser | ReadOnly]
    queryset = Product.objects.all()
    serializer_classes = {
        'create': ProductCreateSerializer,
        'update': ProductCreateSerializer,
        'partial_update': ProductCreateSerializer,
        'destroy': ProductCreateSerializer,
        'retrieve': ProductDetailsSerializer,
    }
    default_serializer_class = ProductShowSerializer

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)


class IsCommentOwner(BasePermission):
    # for view permission
    def has_permission(self, request, view):
        return True

    # for object level permissions
    def has_object_permission(self, request, view, comment):
        return request.method in SAFE_METHODS or comment.user.id == request.user.id or request.user.is_staff


class CommentViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, IsCommentOwner]
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


class AdminOrNotCheckedOut(BasePermission):
    # for object level permissions
    def has_object_permission(self, request, view, order):
        return (order.user.id == request.user.id
                and (
                    (request.method not in SAFE_METHODS
                     and order.checkout_date == None)
                    or request.method in SAFE_METHODS)) \
               or request.user.is_staff


class AdminOrOwner(BasePermission):
    # for object level permissions
    def has_object_permission(self, request, view, order):
        return order.user.id == request.user.id or request.user.is_staff


class OrderViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.DestroyModelMixin,
                   GenericViewSet):
    permission_classes = [IsAuthenticated, AdminOrNotCheckedOut]
    serializer_class = OrderSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, AdminOrOwner])
    def checkout(self, request, pk=None):
        order = self.get_object()
        if order.checkout_date:
            return Response({'checkout': 'Order is already checked out'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            order.checkout_date = timezone.now().date()
            order_items = OrderItem.objects.filter(order=order.id)
            price = 0
            for order_item in order_items:
                order_item.discount = Product.objects.get(id=order_item.product.id).discount
                order_item.price = Product.objects.get(id=order_item.product.id).price
                order_item.save()
                price += order_item.price * order_item.quantity * (100 - order_item.discount) / 100
            order.price = price
            order.save()

        return Response(OrderSerializer(order).data)


class AdminOrNotCheckedOutOrder(BasePermission):
    def has_permission(self, request, view):
        order_pk = request.parser_context['kwargs']['order_pk']
        order = Order.objects.get(id=order_pk)
        user_is_owner = order.user.id == request.user.id
        is_safe_method = request.method in SAFE_METHODS
        order_not_checked_out = order.checkout_date is None
        return request.user.is_staff or \
               (user_is_owner and (is_safe_method or (not is_safe_method and order_not_checked_out)))

    def has_object_permission(self, request, view, order_item):
        user_is_owner =  order_item.order.user.id == request.user.id
        is_safe_method = request.method in SAFE_METHODS
        order_not_checked_out = order_item.order.checkout_date is None
        return request.user.is_staff or \
               (user_is_owner and (is_safe_method or (not is_safe_method and order_not_checked_out)))


class OrderItemViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, AdminOrNotCheckedOutOrder]
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

    def perform_destroy(self, instance):
        if instance.order.checkout_date is None:
            instance.delete()
        else:
            instance.delete()
            order = instance.order
            order_items = OrderItem.objects.filter(order=order.id)
            price = 0
            for order_item in order_items:
                price += order_item.price \
                         * order_item.quantity * (100 - order_item.discount) / 100
            order.price = price
            order.save()

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

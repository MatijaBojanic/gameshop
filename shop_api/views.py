from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from .serializers import ProductShowSerializer, ProductDetailsSerializer, ProductCreateSerializer, CommentSerializer, \
    CategoryShowSerializer, \
    CategoryCreateSerializer, OrderSerializer, OrderItemSerializer, WishListShowSerializer, WishListCreateSerializer, \
    ProductMediaSerializer
from .models import Product, Comment, Category, Order, OrderItem, WishList, ProductMedia
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser
from auth.permissions import ReadOnly, IsCommentOwner,AdminOrNotCheckedOut, AdminOrNotCheckedOutOrder, AdminOrOwner
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, mixins
from django.utils import timezone
from .paginators import ProductPaginator
# Create your views here.


class ProductMediaViewSet(ModelViewSet):
    permission_classes = [IsAdminUser | ReadOnly]
    serializer_class = ProductMediaSerializer
    queryset = ProductMedia.objects.all()

    def get_queryset(self, *args, **kwargs):
        product_id = self.kwargs.get("product_pk")
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise NotFound('A product with this id does not exist')
        return self.queryset.filter(product=product)

    def perform_create(self, serializer):
        serializer.save(product=Product.objects.get(id=self.kwargs.get("product_pk")))


class ProductViewSet(ModelViewSet):
    permission_classes = [IsAdminUser | ReadOnly]
    pagination_class = ProductPaginator
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

    def get_queryset(self):
        """
        If given param name, we filter by it.
        If given order desc, sort by descending.
        If given categories, we are looking for products that have one of the categories.
        In case that a category is a parent category, we also fetch categories that are children of given
        categories.


        :return:
        """
        queryset = Product.objects.all().order_by('price')

        name = self.request.query_params.get('name')
        if name is not None:
            queryset = queryset.filter(name__icontains=name)

        order = self.request.query_params.get('order')
        if order == 'desc':
            queryset = queryset.order_by('-price')

        categories = self.request.GET.get("categories", "")

        if categories is not None:
            categories = categories.split(",")
            children = []

            for category in categories:
                if category.isdigit():
                    children_categories = list(Category.objects.filter(parent=category).values_list('id', flat=True))
                    children = children + children_categories
                else:
                    categories.remove(category)

            categories = categories + children
            if categories:
                queryset = queryset.filter(categories__in=categories)

        return queryset


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
            order.save()
            order.calculate_prices()

        return Response(OrderSerializer(order).data)


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
            order.calculate_prices(False)


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

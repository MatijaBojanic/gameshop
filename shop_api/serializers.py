from .models import Product, Comment, User, Category, OrderItem, Order, WishList, ProductMedia
from rest_framework import serializers
from django.db.models import Avg


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class CategoryShowSerializer(serializers.ModelSerializer):
    parent = SubCategorySerializer()

    class Meta:
        model = Category
        fields = '__all__'


class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMedia
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class ProductShowSerializer(serializers.ModelSerializer):
    """
    Shows product, by loading category name instead of showing its id
    """
    categories = CategoryShowSerializer(many=True)
    media = ProductMediaSerializer(many=True)
    review_score = serializers.SerializerMethodField('get_review_score')

    def get_review_score(self, obj):
        return Comment.objects.filter(product=obj.id).aggregate(Avg('review_score'))['review_score__avg'] or 0

    class Meta:
        model = Product
        fields = '__all__'


class ProductDetailsSerializer(serializers.ModelSerializer):
    """
    Shows product, by loading category name instead of showing its id
    """
    categories = CategoryShowSerializer(many=True)
    media = ProductMediaSerializer(many=True)
    comments = CommentSerializer(many=True)
    review_score = serializers.SerializerMethodField('get_review_score')

    def get_review_score(self, obj):
        return Comment.objects.filter(product=obj.id).aggregate(Avg('review_score'))['review_score__avg'] or 0

    class Meta:
        model = Product
        fields = '__all__'


class ProductCreateSerializer(serializers.ModelSerializer):
    """
    Instead of requiring a dictionary for setting up category relations, here we enable creation by category id
    """
    media = ProductMediaSerializer(source='media_set', many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

    def create(self, validated_data):
        media_data = self.context.get('view').request.FILES
        categories = validated_data.pop('categories', [])
        product = Product.objects.create(**validated_data)
        product.categories.set(categories)
        for single_media_data in media_data:
            file_data = media_data[single_media_data]
            ProductMedia.objects.create(product=product, media=file_data)
        return product


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['id',
                   'is_superuser',
                   'is_staff',
                   'is_active',
                   'password',
                   'email',
                   'first_name',
                   'last_name',
                   'last_login']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['user']

    def create(self, validated_data):
        if Order.objects.filter(user=self.context["request"].user,
                                checkout_date=None).exists():
            return Order.objects.get(user=self.context["request"].user,
                                checkout_date=None)
        user_attributes = Order.objects.create(**validated_data)
        return user_attributes


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'


class WishListShowSerializer(serializers.ModelSerializer):
    products = ProductCreateSerializer(many=True)

    class Meta:
        model = WishList
        fields = '__all__'


class WishListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishList
        fields = '__all__'


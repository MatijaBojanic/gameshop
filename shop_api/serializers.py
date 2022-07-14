from .models import Product, Comment, User, Category, OrderItem, Order
from rest_framework import serializers


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


class ProductShowSerializer(serializers.ModelSerializer):
    """
    Shows product, by loading category name instead of showing its id
    """
    categories = CategoryShowSerializer(many=True)

    class Meta:
        model = Product
        fields = '__all__'


class ProductCreateSerializer(serializers.ModelSerializer):
    """
    Instead of requiring a dictionary for setting up category relations, here we enable creation by category id
    """

    class Meta:
        model = Product
        fields = '__all__'


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


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

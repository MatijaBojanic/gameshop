from .models import Product, Comment, User, Category, OrderItem, Order, WishList, ProductMedia
from rest_framework import serializers, fields
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
    categories = CategoryShowSerializer(many=True)
    media = ProductMediaSerializer(many=True)
    review_score = serializers.SerializerMethodField('get_review_score')

    def get_review_score(self, obj):
        return Comment.objects.filter(product=obj.id).aggregate(Avg('review_score'))['review_score__avg'] or 0

    class Meta:
        model = Product
        fields = '__all__'


class ProductDetailsSerializer(serializers.ModelSerializer):
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


class OrderItemSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField('get_price')
    discount = serializers.SerializerMethodField('get_discount')

    def get_price(self, obj):
        if obj.order.checkout_date:
            return obj.price
        return Product.objects.get(id=obj.product.id).price

    def get_discount(self, obj):
        if obj.order.checkout_date:
            return obj.discount
        return Product.objects.get(id=obj.product.id).discount

    def update(self, instance, validated_data):
        if instance.order.checkout_date is None:
            return super(OrderItemSerializer, self).update(instance, validated_data)
        else:
            instance.price = self.initial_data.get("price", instance.price)
            instance.discount = self.initial_data.get("discount", instance.discount)
            instance.quantity = self.initial_data.get("quantity", instance.quantity)
            instance.product_id = self.initial_data.get("product_id", instance.product_id)
            instance.save()
            item = super(OrderItemSerializer, self).update(instance, validated_data)
            order = instance.order
            order_items = OrderItem.objects.filter(order=order.id)
            price = 0
            for order_item in order_items:
                price += order_item.price \
                         * order_item.quantity * (100 - order_item.discount) / 100
            order.price = price
            order.save()
            return item

    def create(self, validated_data):
        print('test')
        order = validated_data['order']
        print(order.checkout_date)
        if order.checkout_date is None:
            return super(OrderItemSerializer, self).create(validated_data)
        else:
            item = super(OrderItemSerializer, self).create(validated_data)
            item.price = self.initial_data.get("price", item.price)
            item.discount = self.initial_data.get("discount", item.discount)
            item.quantity = self.initial_data.get("quantity", item.quantity)
            item.product_id = self.initial_data.get("product_id", item.product_id)
            item.save()
            order_items = OrderItem.objects.filter(order=order.id)
            price = 0
            for order_item in order_items:
                price += order_item.price \
                         * order_item.quantity * (100 - order_item.discount) / 100
            order.price = price
            order.save()
            return item


    class Meta:
        model = OrderItem
        fields = '__all__'
        read_only_fields = ['price', 'discount']


class OrderSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField('get_price')
    order_items = OrderItemSerializer(many=True, read_only=True)

    def get_price(self, obj):
        if obj.checkout_date:
            return obj.price
        order_items = OrderItem.objects.filter(order=obj.id)
        price = 0
        for order_item in order_items:
            price += Product.objects.get(id=order_item.product.id).price \
                     * order_item.quantity * \
                     (100 - Product.objects.get(id=order_item.product.id).discount) / 100
        return price

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['price']

    def create(self, validated_data):
        if Order.objects.filter(user=self.context["request"].user,
                                checkout_date=None).exists():
            return Order.objects.get(user=self.context["request"].user,
                                checkout_date=None)
        user_attributes = Order.objects.create(**validated_data)
        return user_attributes


class WishListShowSerializer(serializers.ModelSerializer):
    products = ProductShowSerializer(many=True)

    class Meta:
        model = WishList
        fields = '__all__'
        read_only_fields = ['id','user']


class WishListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishList
        fields = '__all__'
        read_only_fields=['id','user']



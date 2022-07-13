from .models import Product, Comment, User
from rest_framework import serializers


class ProductSerializer(serializers.ModelSerializer):
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

    # If we are creating a comment object, we use user as the foreign key. If we are displaying a comment, we are
    # showing its username value, instead FK id.
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['user'] = UserSerializer(instance.user).data.get('username')
        return response

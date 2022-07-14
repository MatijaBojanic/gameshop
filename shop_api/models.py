from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Category(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self',
                               on_delete=models.CASCADE,
                               related_name='child_categories',
                               related_query_name='child_categories',
                               null=True)


class Product(models.Model):
    name = models.CharField(max_length=255)
    content = models.TextField()
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)
    categories = models.ManyToManyField(Category,
                                        related_name='categories',
                                        related_query_name='categories')

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.name


class Comment(models.Model):
    content = models.TextField()
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE,
                                related_name='comments',
                                related_query_name='comment')
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='comments',
                             related_query_name='comment')
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)
    review_score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MaxValueValidator(5), MinValueValidator(1)])

    def __str__(self):
        return self.content


class Order(models.Model):
    checkout_date = models.DateField(null=True)
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='orders',
                             related_query_name='orders')


class OrderItem(models.Model):
    discount = models.DecimalField(decimal_places=2,
                                   max_digits=3,
                                   validators=[MaxValueValidator(100), MinValueValidator(0)])
    quantity = models.IntegerField(validators=[MinValueValidator(0)])
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE,
                                related_name='order_items',
                                related_query_name='order_items')
    order = models.ForeignKey(Order,
                              on_delete=models.CASCADE,
                              related_name='order_items',
                              related_query_name='order_items')

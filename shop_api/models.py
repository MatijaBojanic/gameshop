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
    price = models.DecimalField(decimal_places=4, max_digits=15, default=0)
    discount = models.DecimalField(decimal_places=2,
                                   max_digits=5,
                                   default=0,
                                   validators=[MaxValueValidator(100), MinValueValidator(0)])
    categories = models.ManyToManyField(Category,
                                        related_name='categories',
                                        related_query_name='categories')

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.name


class ProductMedia(models.Model):
    media = models.FileField(upload_to='media/')
    product = models.ForeignKey(Product,
                                  on_delete=models.CASCADE,
                                  related_name='media',
                                  related_query_name='media',
                                  blank=True)

    def __str__(self):
        return self.media.name


class Comment(models.Model):
    content = models.TextField()
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE,
                                related_name='comments',
                                related_query_name='comment',
                                blank=True)
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='comments',
                             related_query_name='comment',
                             blank=True)
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
                             related_query_name='orders',
                             blank=True)
    price = models.DecimalField(decimal_places=4, max_digits=15, default=0)

    def calculate_prices(self, refresh_order_info=True):
        """
        When the order gets checked_out, price and discount need to be fetched from the related product entity of each
        order item, and locked. This way we lock the state of each order item to that specific point in time, i.e. the
        checkout_date.
        After that, we need to calculate the order price by summing each order_item.
        Users can not change orders and order_items after the order gets checked out.

        However, an admin can. In case an admin adds, delete, or changes the order_item we need to recalculate the order
        price as well. But in case of edits, we need not re-fetch info from products as they will not be relevant.
        (They could be changed in the period between the edit and the checkout_date)
        :param refresh_order_info:
        :return:
        """
        order_items = OrderItem.objects.filter(order=self.id)
        price = 0
        for order_item in order_items:
            if refresh_order_info:
                order_item.discount = Product.objects.get(id=order_item.product.id).discount
                order_item.price = Product.objects.get(id=order_item.product.id).price
                order_item.save()
            price += order_item.price * order_item.quantity * (100 - order_item.discount) / 100
        self.price = price
        self.save()


class OrderItem(models.Model):
    discount = models.DecimalField(decimal_places=2,
                                   max_digits=5,
                                   default=0,
                                   validators=[MaxValueValidator(100), MinValueValidator(0)])
    quantity = models.IntegerField(validators=[MinValueValidator(0)])
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE,
                                related_name='order_items',
                                related_query_name='order_items')
    order = models.ForeignKey(Order,
                              on_delete=models.CASCADE,
                              related_name='order_items',
                              related_query_name='order_items',
                              blank=True)
    price = models.DecimalField(decimal_places=4, max_digits=15, default=0)


class WishList(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='wish_list',
                             related_query_name='wish_list',
                             blank=True)
    products = models.ManyToManyField(Product,
                                      related_name='products',
                                      related_query_name='products')

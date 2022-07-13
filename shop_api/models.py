from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Product(models.Model):
    name = models.CharField(max_length=255)
    content = models.TextField()
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

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
        validators=[MaxValueValidator(5), MinValueValidator(1)]
    )

    def __str__(self):
        return self.content

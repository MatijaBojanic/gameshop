# Generated by Django 4.0.6 on 2022-07-24 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop_api', '0011_remove_product_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.FileField(blank=True, upload_to='product_media'),
        ),
    ]

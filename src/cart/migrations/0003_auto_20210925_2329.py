# Generated by Django 3.2.6 on 2021-09-25 17:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0002_alter_cartitem_cart'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartitem',
            name='unit_discount',
        ),
        migrations.RemoveField(
            model_name='cartitem',
            name='unit_price',
        ),
    ]

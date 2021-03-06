# Generated by Django 3.2.6 on 2021-09-08 16:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shop', '0015_reviewreaction'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('mobile', models.CharField(max_length=15)),
                ('shipping', models.TextField(max_length=500)),
                ('billing', models.TextField(max_length=500)),
                ('status', models.CharField(choices=[('PL', 'Placed'), ('CU', 'Cancelled By User'), ('CN', 'Cancelled'), ('PK', 'Packed'), ('TN', 'In Transit'), ('DV', 'Delivered'), ('RI', 'Return Initiated'), ('RC', 'Return Completed')], max_length=2)),
                ('item_total', models.FloatField()),
                ('discount', models.FloatField()),
                ('tax', models.FloatField()),
                ('grand_total', models.FloatField()),
                ('created', models.DateTimeField(editable=False)),
                ('modified', models.DateTimeField()),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_owner', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderRefund',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('refund_status', models.CharField(choices=[('RI', 'Refund Initated'), ('RC', 'Refund Completed')], max_length=2)),
                ('created', models.DateTimeField(editable=False)),
                ('modified', models.DateTimeField()),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.order')),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qty', models.IntegerField()),
                ('unit_price', models.FloatField()),
                ('created', models.DateTimeField(editable=False)),
                ('modified', models.DateTimeField()),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.product')),
            ],
        ),
        migrations.CreateModel(
            name='OrderActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_status', models.CharField(blank=True, max_length=2, null=True)),
                ('to_status', models.CharField(max_length=2)),
                ('created', models.DateTimeField(editable=False)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.order')),
            ],
        ),
    ]

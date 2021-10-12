# Generated by Django 3.2.6 on 2021-08-28 10:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shop', '0006_brand'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=80)),
                ('legacy_sku', models.CharField(blank=True, max_length=50, null=True)),
                ('code', models.CharField(max_length=3)),
                ('description', models.TextField(max_length=500)),
                ('listing_date', models.DateTimeField()),
                ('is_active', models.BooleanField(default=True)),
                ('qty', models.IntegerField()),
                ('maximum_retail_price', models.FloatField()),
                ('listing_price', models.FloatField()),
                ('additional_discount', models.FloatField(default=0.0)),
                ('slug', models.SlugField()),
                ('created', models.DateTimeField(editable=False)),
                ('modified', models.DateTimeField()),
                ('brand', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='shop.brand')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='shop.category')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='prd_creator', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='prd_modifier', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Products',
            },
        ),
    ]
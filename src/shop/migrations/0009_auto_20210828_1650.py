# Generated by Django 3.2.6 on 2021-08-28 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0008_productattribute'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='abr',
            field=models.CharField(default='XXX', max_length=4),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='primarycategory',
            name='abr',
            field=models.CharField(default='XXX', max_length=4),
            preserve_default=False,
        ),
    ]
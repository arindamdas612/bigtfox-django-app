# Generated by Django 3.2.6 on 2021-08-26 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_auto_20210826_1804'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraddress',
            name='type',
            field=models.CharField(choices=[('Rs', 'Residence'), ('Of', 'Office'), ('Ot', 'Others')], max_length=2),
        ),
    ]

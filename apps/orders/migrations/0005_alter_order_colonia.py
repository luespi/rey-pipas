# Generated by Django 5.0.2 on 2025-07-08 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_order_colonia_order_zone_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='colonia',
            field=models.CharField(max_length=120, verbose_name='Colonia (opcional)'),
        ),
    ]

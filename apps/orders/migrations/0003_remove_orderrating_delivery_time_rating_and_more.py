# Generated by Django 5.0.2 on 2025-06-17 05:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderrating',
            name='delivery_time_rating',
        ),
        migrations.RemoveField(
            model_name='orderrating',
            name='operator_service_rating',
        ),
        migrations.RemoveField(
            model_name='orderrating',
            name='water_quality_rating',
        ),
    ]

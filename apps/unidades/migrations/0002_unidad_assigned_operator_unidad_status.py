# Generated by Django 5.0.2 on 2025-07-15 01:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('unidades', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='unidad',
            name='assigned_operator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='unidades', to=settings.AUTH_USER_MODEL, verbose_name='Operador asignado'),
        ),
        migrations.AddField(
            model_name='unidad',
            name='status',
            field=models.CharField(choices=[('active', 'Activa'), ('inactive', 'Inactiva')], default='active', max_length=8, verbose_name='Estado'),
        ),
    ]

# Generated by Django 5.0.2 on 2025-07-14 22:13

import apps.unidades.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Unidad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('capacidad_litros', models.PositiveIntegerField(verbose_name='Capacidad del tanque (L)')),
                ('numero_placas', models.CharField(max_length=15, unique=True, verbose_name='Número de placas')),
                ('foto_frontal', models.ImageField(upload_to=apps.unidades.models.unidad_upload_path, verbose_name='Foto frontal')),
                ('foto_lateral', models.ImageField(upload_to=apps.unidades.models.unidad_upload_path, verbose_name='Foto lateral')),
                ('verificacion', models.ImageField(upload_to=apps.unidades.models.unidad_upload_path, verbose_name='Verificación vehicular')),
                ('tarjeta_circul', models.ImageField(upload_to=apps.unidades.models.unidad_upload_path, verbose_name='Tarjeta de circulación')),
                ('poliza_seguro', models.ImageField(upload_to=apps.unidades.models.unidad_upload_path, verbose_name='Póliza de seguro')),
                ('constancia_repuve', models.ImageField(upload_to=apps.unidades.models.unidad_upload_path, verbose_name='Constancia REPUVE')),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('actualizado', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Unidad',
                'verbose_name_plural': 'Unidades',
            },
        ),
    ]

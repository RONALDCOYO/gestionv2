# Generated by Django 5.0.7 on 2024-10-29 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0020_correspondencia_fecha_limite_respuesta'),
    ]

    operations = [
        migrations.AddField(
            model_name='dependencia',
            name='inicio_consecutivo',
            field=models.IntegerField(default=1),
        ),
    ]

# Generated by Django 5.0.7 on 2024-10-30 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0023_rename_consecutivo_correspondencia_numero_consecutivo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='correspondencia',
            name='numero_consecutivo',
        ),
        migrations.AddField(
            model_name='correspondencia',
            name='consecutivo',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]

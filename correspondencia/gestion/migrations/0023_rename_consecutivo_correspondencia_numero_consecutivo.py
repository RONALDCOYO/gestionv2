# Generated by Django 5.0.7 on 2024-10-29 20:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0022_alter_correspondencia_consecutivo'),
    ]

    operations = [
        migrations.RenameField(
            model_name='correspondencia',
            old_name='consecutivo',
            new_name='numero_consecutivo',
        ),
    ]

# Generated by Django 5.1.1 on 2024-09-13 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0007_alter_perfilusuario_empresa'),
    ]

    operations = [
        migrations.CreateModel(
            name='gestion_empresa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
            ],
        ),
        migrations.DeleteModel(
            name='Profile',
        ),
    ]

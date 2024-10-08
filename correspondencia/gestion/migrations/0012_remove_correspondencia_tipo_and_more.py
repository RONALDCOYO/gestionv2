# Generated by Django 5.1.1 on 2024-09-20 19:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0011_alter_correspondencia_documento_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='correspondencia',
            name='tipo',
        ),
        migrations.AddField(
            model_name='correspondencia',
            name='tipo_correspondencia',
            field=models.CharField(choices=[('Carta', 'Carta'), ('Memorando', 'Memorando'), ('Email', 'Email')], default='Carta', max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='correspondencia',
            name='fecha',
            field=models.DateField(),
        ),
    ]

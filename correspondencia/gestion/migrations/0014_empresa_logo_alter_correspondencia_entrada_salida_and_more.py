# Generated by Django 5.1.1 on 2024-09-25 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0013_rename_texto_respuesta_respuestacorrespondencia_respuesta_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='empresa',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='logos_empresas/'),
        ),
        migrations.AlterField(
            model_name='correspondencia',
            name='entrada_salida',
            field=models.CharField(choices=[('Entrada', 'Entrada'), ('Salida', 'Salida')], max_length=10),
        ),
        migrations.AlterField(
            model_name='correspondencia',
            name='tipo_correspondencia',
            field=models.CharField(choices=[('Carta', 'Carta'), ('Memorando', 'Memorando'), ('Email', 'Email'), ('DP', 'DP')], max_length=20),
        ),
    ]

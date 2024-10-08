from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone



class Empresa(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10)
    logo = models.ImageField(upload_to='logos_empresas/', null=True, blank=True)  # Campo para la imagen del logo

    def __str__(self):
        return self.nombre
    
from django.db import models


class Dependencia(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

class gestion_empresa(models.Model):
    nombre = models.CharField(max_length=100)  # Campo para el nombre de la empresa

    def __str__(self):
        return self.nombre  # Esto permitirá que el nombre de la empresa se muestre en el formulario

    
class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    empresas = models.ManyToManyField(Empresa, blank=True)  # Ahora un usuario puede estar en varias empresas
    dependencias = models.ManyToManyField(Dependencia, blank=True)

    def __str__(self):
        return f"{self.user.username} - {', '.join([empresa.nombre for empresa in self.empresas.all()])}"




    

class Correspondencia(models.Model):
    TIPO_CORRESPONDENCIA = [
        ('Carta', 'Carta'),
        ('Memorando', 'Memorando'),
        ('Email', 'Email'),
        ('DP', 'DP'),
    ]

    ENTRADA_SALIDA = [
        ('Entrada', 'Entrada'),
        ('Salida', 'Salida'),
        
    ]

    entrada_salida = models.CharField(max_length=10, choices=ENTRADA_SALIDA)
    tipo_correspondencia = models.CharField(max_length=20, choices=TIPO_CORRESPONDENCIA)
    consecutivo = models.CharField(max_length=100)
    dependencia = models.ForeignKey(Dependencia, on_delete=models.CASCADE)
    fecha = models.DateField(null=False)
    documento = models.FileField(upload_to='correspondencias/', null=True, blank=True)
    asunto = models.CharField(max_length=255)
    remitente = models.CharField(max_length=255)
    destinatario = models.CharField(max_length=255)
    necesita_respuesta = models.BooleanField(default=False)
    respondida = models.BooleanField(default=False)  # Nuevo campo
    respuesta = models.TextField(blank=True, null=True)  # Campo para almacenar la respuesta
    fecha_respuesta = models.DateTimeField(null=True, blank=True)  # Fecha de respuesta
    documento_respuesta = models.FileField(upload_to='respuestas/', null=True, blank=True)  # Campo para el documento de respuesta
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    def marcar_como_respondida(self, respuesta_texto):
        """Marca la correspondencia como respondida y almacena la respuesta"""
        self.respondida = True
        self.respuesta = respuesta_texto
        self.fecha_respuesta = timezone.now()
        self.save()
    def __str__(self):
        return self.consecutivo


class RespuestaCorrespondencia(models.Model):
    correspondencia = models.ForeignKey(Correspondencia, on_delete=models.CASCADE)
    respuesta = models.TextField()
    fecha_respuesta = models.DateField()
    documento_respuesta = models.FileField(upload_to='respuestas/', null=True, blank=True)  # Nuevo campo para el documento

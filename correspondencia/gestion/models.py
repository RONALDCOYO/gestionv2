from django.contrib.auth.models import User
from django.db import models



class Empresa(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10)

    def __str__(self):
        return self.nombre
    
from django.db import models

class gestion_empresa(models.Model):
    nombre = models.CharField(max_length=100)  # Campo para el nombre de la empresa

    def __str__(self):
        return self.nombre  # Esto permitirá que el nombre de la empresa se muestre en el formulario

    
class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Asegúrate de que el campo se llame 'user'
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.user.username} - {self.empresa.nombre}"



class Dependencia(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

class Correspondencia(models.Model):
    TIPO_CORRESPONDENCIA = [
        ('Carta', 'Carta'),
        ('Memorando', 'Memorando'),
        ('Email', 'Email'),
    ]
    tipo = models.CharField(max_length=10, choices=TIPO_CORRESPONDENCIA)
    dependencia = models.ForeignKey(Dependencia, on_delete=models.CASCADE)
    entrada_salida = models.CharField(max_length=10)
    documento = models.FileField(upload_to='documentos/')
    fecha = models.DateField(null=False)
    consecutivo = models.CharField(max_length=50)
    user= models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    def __str__(self):
        return self.consecutivo

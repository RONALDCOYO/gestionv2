from django.contrib.auth.models import User
from django.db import models





class Empresa(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10)

    def __str__(self):
        return self.nombre
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username    

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
    #fecha = models.DateTimeField(auto_now_add=True)
    fecha = models.DateField(null=False)
    consecutivo = models.CharField(max_length=50)

    def __str__(self):
        return self.consecutivo

from django.contrib import admin
from django.contrib import admin
from .models import Empresa, PerfilUsuario, Dependencia  # Importa tus modelos

# Registra tus modelos en el admin
admin.site.register(Empresa)
admin.site.register(PerfilUsuario)
admin.site.register(Dependencia)

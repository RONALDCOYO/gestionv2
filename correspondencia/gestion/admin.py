from django.contrib import admin
from django.contrib import admin
from .models import Empresa, Profile, Dependencia  # Importa tus modelos

# Registra tus modelos en el admin
admin.site.register(Empresa)
admin.site.register(Profile)
admin.site.register(Dependencia)

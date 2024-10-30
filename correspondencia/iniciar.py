# iniciar.py

import os
import django

# Configurar las variables de entorno
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'correspondencia.settings')
django.setup()

from gestion.models import Dependencia, Empresa

# Obtener las empresas existentes
grodco = Empresa.objects.get(nombre="Grodco")

# Configurar el inicio del consecutivo para las dependencias
Dependencia.objects.filter(nombre="Jurídica", empresa=grodco).update(inicio_consecutivo=36)

print("Configuración de inicio del consecutivo completada.")

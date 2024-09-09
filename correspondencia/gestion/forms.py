from django import forms
from .models import Correspondencia
from django import forms
from .models import Dependencia

class CorrespondenciaForm(forms.ModelForm):
    class Meta:
        model = Correspondencia
        fields = ['tipo', 'fecha', 'dependencia', 'documento', 'entrada_salida']

class DependenciaForm(forms.ModelForm):
    class Meta:
        model = Dependencia
        fields = ['nombre', 'codigo', 'empresa']
from django.contrib.auth.models import User
from django import forms
from .models import Correspondencia
from django import forms
from .models import PerfilUsuario, Empresa, Dependencia

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nombre', 'codigo']



class CorrespondenciaForm(forms.ModelForm):
    
    fecha = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    
    class Meta:
        model = Correspondencia
        fields = ['tipo_correspondencia', 'dependencia', 'entrada_salida', 'fecha', 'documento', 'asunto', 'remitente', 'destinatario', 'necesita_respuesta']

    def __init__(self, *args, **kwargs):
        # Pasar el usuario desde la vista al formulario
        user = kwargs.pop('user', None)
        super(CorrespondenciaForm, self).__init__(*args, **kwargs)

        if user:
            # Obtener el perfil del usuario
            try:
                perfil = PerfilUsuario.objects.get(user=user)
                empresa = perfil.empresa
                # Filtrar las dependencias por la empresa del usuario
                self.fields['dependencia'].queryset = Dependencia.objects.filter(empresa=empresa)
            except PerfilUsuario.DoesNotExist:
                # Si el perfil no existe y el usuario es superusuario, mostrar todas las dependencias
                if user.is_superuser:
                    self.fields['dependencia'].queryset = Dependencia.objects.all()
                else:
                    # De lo contrario, no permitir la selección de dependencias
                    self.fields['dependencia'].queryset = Dependencia.objects.none()

          # Agregar clases de Bootstrap a todos los widgets
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'           




class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Correspondencia
        fields = ['documento']  # Solo incluimos el campo 'documento'



class RespuestaCorrespondenciaForm(forms.ModelForm):
    class Meta:
        model = Correspondencia
        fields = ['respuesta']

    def save(self, commit=True):
        correspondencia = super().save(commit=False)
        correspondencia.marcar_como_respondida(self.cleaned_data['respuesta'])
        if commit:
            correspondencia.save()
        return correspondencia
    

class DependenciaForm(forms.ModelForm):
    class Meta:
        model = Dependencia
        fields = ['nombre', 'codigo', 'empresa']


class RegistroUsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    empresa = forms.ModelChoiceField(queryset=Empresa.objects.all(), label="Empresa")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # Encripta la contraseña
        if commit:
            user.save()
            PerfilUsuario.objects.create(user=user, empresa=self.cleaned_data['empresa'])  # Crea el perfil de usuario y asocia la empresa
        return user
    


    


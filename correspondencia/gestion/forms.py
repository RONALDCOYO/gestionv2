from django.contrib.auth.models import User
from django import forms
from .models import Correspondencia, RespuestaCorrespondencia
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
        user = kwargs.pop('user', None)
        empresa_id = kwargs.pop('empresa_id', None)
        super(CorrespondenciaForm, self).__init__(*args, **kwargs)

        if user and empresa_id:
            try:
                perfil = PerfilUsuario.objects.get(user=user)
                if not user.is_superuser:
                    # Filtrar dependencias por empresa y perfil de usuario
                    self.fields['dependencia'].queryset = Dependencia.objects.filter(
                        empresa_id=empresa_id, perfilusuario__user=user
                    ).distinct()
                else:
                    # Si es superusuario, puede ver todas las dependencias de la empresa
                    self.fields['dependencia'].queryset = Dependencia.objects.filter(
                        empresa_id=empresa_id
                    )
            except PerfilUsuario.DoesNotExist:
                self.fields['dependencia'].queryset = Dependencia.objects.none()
        elif user:
            try:
                perfil = PerfilUsuario.objects.get(user=user)
                # Opcional: Filtrar dependencias sin especificar empresa
                self.fields['dependencia'].queryset = perfil.dependencias.all()
            except PerfilUsuario.DoesNotExist:
                self.fields['dependencia'].queryset = Dependencia.objects.none()

        # Aplicar clases de Bootstrap a los widgets del formulario
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'





class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Correspondencia
        fields = ['documento']  # Solo incluimos el campo 'documento'



class RespuestaCorrespondenciaForm(forms.ModelForm):
    class Meta:
        model = Correspondencia
        fields = ['respuesta', 'documento_respuesta']  # Agregamos el campo de documento_respuesta

    def save(self, commit=True):
        correspondencia = super().save(commit=False)
        correspondencia.marcar_como_respondida(self.cleaned_data['respuesta'])
        
        # Si hay un documento cargado, lo asignamos a la correspondencia
        if 'documento_respuesta' in self.cleaned_data:
            correspondencia.documento_respuesta = self.cleaned_data['documento_respuesta']

        if commit:
            correspondencia.save()
        return correspondencia
    

class DependenciaForm(forms.ModelForm):
    class Meta:
        model = Dependencia
        fields = ['nombre', 'codigo', 'empresa']

class RegistroUsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    empresas = forms.ModelMultipleChoiceField(
        queryset=Empresa.objects.all(),
        widget=forms.SelectMultiple,  # SelectMultiple para permitir la selección múltiple
        required=True,
        label="Empresas"
    )
    dependencias = forms.ModelMultipleChoiceField(
        queryset=Dependencia.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Dependencias"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super(RegistroUsuarioForm, self).__init__(*args, **kwargs)
        if 'empresas' in self.data:
            try:
                empresas_ids = self.data.getlist('empresas')
                self.fields['dependencias'].queryset = Dependencia.objects.filter(empresa_id__in=empresas_ids)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['dependencias'].queryset = self.instance.perfilusuario.dependencias.all()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            perfil = PerfilUsuario.objects.create(user=user)
            perfil.empresas.set(self.cleaned_data['empresas'])
            perfil.dependencias.set(self.cleaned_data['dependencias'])
            perfil.save()
        return user
    
class EditarUsuarioForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']  # Agrega más campos si es necesario


    
class FiltroCorrespondenciaForm(forms.Form):
    fecha_inicio = forms.DateField(required=False)
    fecha_fin = forms.DateField(required=False)
    empresa = forms.ModelChoiceField(queryset=Empresa.objects.all(), required=False)
    dependencia = forms.ModelChoiceField(queryset=Dependencia.objects.all(), required=False)
    tipo_correspondencia = forms.ChoiceField(choices=[
        ('', '-- Todas --'),
        ('Carta', 'Carta'),
        ('Memorando', 'Memorando'),
        ('Email', 'Email'),
    ], required=False)
    adjuntos = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(FiltroCorrespondenciaForm, self).__init__(*args, **kwargs)
        if user and not user.is_superuser:
            # Filtrar empresas y dependencias solo asociadas al usuario si no es superuser
            self.fields['empresa'].queryset = Empresa.objects.filter(perfilusuario__user=user)
            # Filtrar dependencias en función de las empresas seleccionadas
            self.fields['dependencia'].queryset = Dependencia.objects.filter(empresa__in=self.fields['empresa'].queryset)
        else:
            # Si es superuser, mostrar todas las empresas y dependencias
            self.fields['empresa'].queryset = Empresa.objects.all()
            self.fields['dependencia'].queryset = Dependencia.objects.all()

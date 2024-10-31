from django.contrib.auth.models import User
from django import forms
from .models import Correspondencia, RespuestaCorrespondencia
from django import forms
from .models import PerfilUsuario, Empresa, Dependencia
from datetime import timedelta



class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nombre', 'codigo']



class CorrespondenciaForm(forms.ModelForm):
    dias_para_responder = forms.IntegerField(
        required=False,
        label="Días para responder", 
        help_text="Define cuántos días tiene el usuario para responder."
    )

    fecha = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Correspondencia
        fields = [
            'tipo_correspondencia',
            'dependencia',
            'entrada_salida', 
            'fecha', 
            'documento', 
            'asunto', 
            'remitente', 
            'destinatario', 
            'necesita_respuesta', 
            'dias_para_responder']

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

    def save(self, commit=True):
        correspondencia = super().save(commit=False)

        # Si se proporcionaron días para responder y la correspondencia necesita respuesta
        if self.cleaned_data.get('dias_para_responder') and self.cleaned_data.get('necesita_respuesta'):
            dias = self.cleaned_data['dias_para_responder']
            # Calcular la fecha límite de respuesta sumando los días a la fecha actual
            correspondencia.fecha_limite_respuesta = correspondencia.fecha + timedelta(days=dias)

        if commit:
            correspondencia.save()

        return correspondencia       





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
        widget=forms.SelectMultiple,
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
                empresas_ids = self.data.getlist('empresas')  # Verifica el nombre del campo 'empresas'
                self.fields['dependencias'].queryset = Dependencia.objects.filter(empresa_id__in=empresas_ids)
            except (ValueError, TypeError):
                self.fields['dependencias'].queryset = Dependencia.objects.none()
        elif self.instance.pk:
            self.fields['dependencias'].queryset = self.instance.perfilusuario.dependencias.all()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            perfil, created = PerfilUsuario.objects.get_or_create(user=user)
            perfil.empresas.set(self.cleaned_data['empresas'])
            perfil.dependencias.set(self.cleaned_data['dependencias'])
            perfil.save()
        return user


class EditarUsuarioForm(forms.ModelForm):
    empresas = forms.ModelMultipleChoiceField(
        queryset=Empresa.objects.all(),
        widget=forms.SelectMultiple,
        required=True,
        label="Empresas"
    )
    dependencias = forms.ModelMultipleChoiceField(
        queryset=Dependencia.objects.all(),
        widget=forms.SelectMultiple,
        required=False,
        label="Dependencias"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super(EditarUsuarioForm, self).__init__(*args, **kwargs)
        if self.instance.pk:  # Si el usuario ya existe
            perfil = PerfilUsuario.objects.get(user=self.instance)
            self.fields['empresas'].initial = perfil.empresas.all()
            self.fields['dependencias'].initial = perfil.dependencias.all()

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            perfil, created = PerfilUsuario.objects.get_or_create(user=user)
            perfil.empresas.set(self.cleaned_data['empresas'])
            perfil.dependencias.set(self.cleaned_data['dependencias'])
            perfil.save()
        return user

    
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

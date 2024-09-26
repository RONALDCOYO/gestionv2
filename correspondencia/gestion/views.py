from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate, logout
from django.core.files.storage import default_storage
from .models import Correspondencia, PerfilUsuario, Empresa
from .forms import DocumentoForm, RegistroUsuarioForm, CorrespondenciaForm, DependenciaForm, EmpresaForm, RespuestaCorrespondenciaForm
from django.contrib.auth.models import User
from django.contrib import messages


# Vista de la página principal (portada)
@login_required
def portada(request):
    try:
        perfil = PerfilUsuario.objects.get(user=request.user)
        empresa = perfil.empresa
    except PerfilUsuario.DoesNotExist:
        empresa = None

    return render(request, 'portada.html', {'empresa': empresa})


# Función para comprobar si el usuario es administrador
def es_admin(user):
    return user.is_superuser


# Vista para registrar empresa (solo admin)
@login_required
@user_passes_test(es_admin)
def registrar_empresa(request):
    if request.method == 'POST':
        form = EmpresaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('portada')  # Redirige a la portada después de registrar la empresa
    else:
        form = EmpresaForm()

    return render(request, 'registrar_empresa.html', {'form': form})

# Vista para registrar correspondencia (disponible para todos los usuarios)
from django.core.exceptions import ObjectDoesNotExist



@login_required
def registro_correspondencia(request):
    try:
        perfil = PerfilUsuario.objects.get(user=request.user)
        empresa = perfil.empresa
    except PerfilUsuario.DoesNotExist:
        if request.user.is_superuser:
            empresa = None
        else:
            # Redirigir a una página de error o mostrar un mensaje si el perfil no existe.
            return redirect('error')  # 'error' esté definido en tus URL

    # Si la solicitud es POST, se procesa el formulario
    if request.method == 'POST':
        form = CorrespondenciaForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            nueva_correspondencia = form.save(commit=False)
            nueva_correspondencia.user = request.user

            # Manejo del documento
            if 'documento' in request.FILES:
                nueva_correspondencia.documento = request.FILES['documento']

            # Generar el consecutivo
            empresa_codigo = nueva_correspondencia.dependencia.empresa.codigo
            dependencia_codigo = nueva_correspondencia.dependencia.codigo
            año = nueva_correspondencia.fecha.year
            ultimo_consecutivo = Correspondencia.objects.filter(
                dependencia=nueva_correspondencia.dependencia,
                fecha__year=año
            ).count() + 1
            consecutivo = f"{empresa_codigo}-{dependencia_codigo}-{año}-{ultimo_consecutivo}"
            nueva_correspondencia.consecutivo = consecutivo

            nueva_correspondencia.save()

            # Mensaje de éxito
            from django.contrib import messages
            messages.success(request, "La correspondencia ha sido registrada con éxito.")

            return redirect('registro_correspondencia')
    else:
        # Si la solicitud es GET, se muestra el formulario vacío
        form = CorrespondenciaForm(user=request.user)

    # Obtener las correspondencias para mostrar en la lista
    if request.user.is_superuser:
        correspondencias = Correspondencia.objects.all().order_by('-fecha')
    else:
        correspondencias = Correspondencia.objects.filter(dependencia__empresa=empresa).order_by('-fecha')

    # Retornar la respuesta asegurándote de que siempre haya un render
    return render(request, 'gestion/registro_correspondencia.html', {
        'form': form,
        'correspondencias': correspondencias,
        'empresa': empresa
    })


   
# Vista para lista la correspondencia

@user_passes_test(lambda u: u.is_superuser)
def lista_correspondencia(request):
    correspondencias = Correspondencia.objects.all()
    context = []

    for correspondencia in correspondencias:
        # Verificar si la correspondencia tiene un documento asociado
        if correspondencia.documento:
            documento_url = correspondencia.documento.url  # Obtener URL si existe
        else:
            documento_url = None  # Asignar None si no hay documento

        context.append({
            'correspondencia': correspondencia,
            'documento_url': documento_url,  # Pasar la URL o None
        })

    return render(request, 'lista_correspondencia.html', {'correspondencias': context})



def responder_correspondencia(request, correspondencia_id):
    correspondencia = get_object_or_404(Correspondencia, id=correspondencia_id)

    if request.method == 'POST':
        form = RespuestaCorrespondenciaForm(request.POST, instance=correspondencia)
        if form.is_valid():
            form.save()
            return redirect('registro_correspondencia')  # Redirige a la lista de correspondencias
    else:
        form = RespuestaCorrespondenciaForm(instance=correspondencia)

    return render(request, 'gestion/responder_correspondencia.html', {'form': form, 'correspondencia': correspondencia})


@login_required
def ver_respuesta(request, correspondencia_id):
    correspondencia = get_object_or_404(Correspondencia, id=correspondencia_id)

    # Solo permitir ver la respuesta si la correspondencia ha sido respondida
    if not correspondencia.respondida:
        messages.error(request, "Esta correspondencia aún no ha sido respondida.")
        return redirect('registro_correspondencia')

    return render(request, 'gestion/ver_respuesta.html', {'correspondencia': correspondencia})

@user_passes_test(es_admin)
def crear_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        empresa_id = request.POST.get('empresa')  # Obtener el ID de la empresa seleccionada

        # Validar que el username y password no estén vacíos
        if not username or not password:
            return render(request, 'registro_usuario.html', {
                'empresas': Empresa.objects.all(),
                'error': 'El nombre de usuario y la contraseña son obligatorios.'
            })

        # Crear el usuario
        nuevo_usuario = User.objects.create_user(username=username, password=password)

        # Asociar el usuario con la empresa
        empresa = Empresa.objects.get(id=empresa_id)
        perfil = PerfilUsuario(user=nuevo_usuario, empresa=empresa)
        perfil.save()
     
        return redirect('portada')  # Redirige a la portada después de crear el usuario

    # Pasar las empresas al contexto para usarlas en el formulario
    empresas = Empresa.objects.all()
    return render(request, 'registro_usuario.html', {'empresas': empresas})


# Vista del index (registro de correspondencia)
@login_required
def index(request):
    try:
        perfil_usuario = PerfilUsuario.objects.get(user=request.user)
        empresa = perfil_usuario.empresa
    except PerfilUsuario.DoesNotExist:
        # Redirigir o mostrar un mensaje si no existe el perfil
        return render(request, 'gestion/error.html', {
            'mensaje': 'No se encontró el perfil del usuario.'
        })

    if request.method == 'POST':
        form = CorrespondenciaForm(request.POST, request.FILES)
        if form.is_valid():
            nueva_correspondencia = form.save(commit=False)
            # Generar el consecutivo basado en la empresa y dependencia
            empresa_codigo = nueva_correspondencia.dependencia.empresa.codigo
            dependencia_codigo = nueva_correspondencia.dependencia.codigo
            año = nueva_correspondencia.fecha.year
            # Obtener el último consecutivo para la misma empresa y dependencia
            ultimo_consecutivo = Correspondencia.objects.filter(
                dependencia=nueva_correspondencia.dependencia,
                fecha__year=año
            ).count() + 1

            consecutivo = f"{empresa_codigo}-{dependencia_codigo}-{año}-{ultimo_consecutivo}"
            nueva_correspondencia.consecutivo = consecutivo
            nueva_correspondencia.user = request.user
            nueva_correspondencia.save()

            return redirect('index')
    else:
        form = CorrespondenciaForm()

    correspondencias = Correspondencia.objects.filter(dependencia__empresa=empresa)

    return render(request, 'gestion/index.html', {
        'form': form,
        'correspondencias': correspondencias,
        'empresa': empresa
    })

# Vista para crear dependencias (solo admin)
@login_required
@user_passes_test(es_admin)
def crear_dependencia(request):
    if request.method == 'POST':
        form = DependenciaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('portada')  # Redirigir al index después de guardar la dependencia
    else:
        form = DependenciaForm()
    return render(request, 'gestion/crear_dependencia.html', {'form': form})

# Vista para registrar usuario (solo admin)
@login_required
@user_passes_test(es_admin)
def registrar_usuario(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('portada')  # Redirige a la página principal
    else:
        form = RegistroUsuarioForm()

    return render(request, 'registro_usuario.html', {'form': form})



@login_required
def adjuntar_documento(request, correspondencia_id):
    # Obtener la instancia de la correspondencia
    correspondencia = get_object_or_404(Correspondencia, id=correspondencia_id)

    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES, instance=correspondencia)

        if form.is_valid():
            # Guardar solo el documento subido
            form.save()
            messages.success(request, 'Documento adjuntado con éxito.')
            return redirect('registro_correspondencia')
    else:
        form = DocumentoForm(instance=correspondencia)

    return render(request, 'gestion/adjuntar_documento.html', {'form': form, 'correspondencia': correspondencia})



# Vista para cerrar sesión
def logout_view(request):
    logout(request)
    return redirect('login')  # Redirigir a la página de portada o la que prefieras después de cerrar sesión

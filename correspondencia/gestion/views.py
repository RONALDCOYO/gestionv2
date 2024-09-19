from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate, logout
from .models import Correspondencia, PerfilUsuario, Empresa
from .forms import RegistroUsuarioForm, CorrespondenciaForm, DependenciaForm, EmpresaForm
from django.contrib.auth.models import User


# Vista de la página principal (portada)
@login_required
def portada(request):
    return render(request, 'portada.html')




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
            return redirect('error')  # Manejar error si el perfil no existe

    correspondencias = Correspondencia.objects.filter(dependencia__empresa=empresa)

    if request.method == 'POST':
        form = CorrespondenciaForm(request.POST, request.FILES, user=request.user)  # Pasar el usuario al formulario
        if form.is_valid():
            nueva_correspondencia = form.save(commit=False)
            nueva_correspondencia.user = request.user

            # Generar consecutivo
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
            return redirect('registro_correspondencia')
    else:
        form = CorrespondenciaForm(user=request.user)  # Pasar el usuario al formulario

    return render(request, 'gestion/registro_correspondencia.html', {
        'form': form,
        'correspondencias': correspondencias
    })

# Vista para lista la correspondencia

@login_required
def lista_correspondencia(request):
    if request.user.is_superuser:
        correspondencias = Correspondencia.objects.all()  # Mostrar todas las correspondencias
    else:
        perfil_usuario = PerfilUsuario.objects.get(user=request.user)
        correspondencias = Correspondencia.objects.filter(dependencia__empresa=perfil_usuario.empresa)  # Filtrar según la empresa del usuario

    return render(request, 'gestion/lista_correspondencia.html', {'correspondencias': correspondencias})


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


# Vista para cerrar sesión
def logout_view(request):
    logout(request)
    return redirect('login')  # Redirigir a la página de portada o la que prefieras después de cerrar sesión

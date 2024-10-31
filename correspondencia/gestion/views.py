import openpyxl
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from .models import Empresa, Dependencia, Correspondencia, PerfilUsuario, User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.core.files.storage import default_storage
from .models import Correspondencia, PerfilUsuario, Empresa, Dependencia
from django.contrib.auth.forms import PasswordChangeForm
from .forms import DocumentoForm, EditarUsuarioForm, RegistroUsuarioForm, CorrespondenciaForm, DependenciaForm, EmpresaForm, RespuestaCorrespondenciaForm, FiltroCorrespondenciaForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count
from datetime import timedelta


# Vista de la página principal (portada)
@login_required
def portada(request):
    # Obtener la empresa seleccionada de la URL
    empresa_id = request.GET.get('empresa_id')

    if empresa_id:
        # Redirigir al registro de correspondencia con el ID de la empresa
        return redirect('registro_correspondencia', empresa_id=empresa_id)

    # Si no hay empresa seleccionada, mostrar la portada
    try:
        perfil = PerfilUsuario.objects.get(user=request.user)
        empresas = perfil.empresas.all()
        dependencias = perfil.dependencias.all()
    except PerfilUsuario.DoesNotExist:
        empresas = []
        dependencias = []

    # Si el usuario es superusuario, obtener todos los usuarios, empresas y dependencias
    if request.user.is_superuser:
        usuarios = User.objects.all()  # Obtener todos los usuarios
        empresas = Empresa.objects.all()  # Obtener todas las empresas
        dependencias = Dependencia.objects.all()  # Obtener todas las dependencias
        correspondencias = Correspondencia.objects.all()
    else:
        usuarios = None
        correspondencias = Correspondencia.objects.filter(dependencia__in=dependencias)  # Correspondencias relacionadas con las dependencias del perfil


    # Renderizar la plantilla de la portada con los datos
    return render(request, 'portada.html', {
        'empresas': empresas,
        'dependencias': dependencias,
        'usuarios': usuarios,  # Pasar los usuarios si es superusuario
        'correspondencias': correspondencias  # Pasar las correspondencias en el contexto
    })


# Función para comprobar si el usuario es administrador
def es_admin(user):
    return user.is_superuser


# Vista para registrar empresa (solo admin)
@login_required
@user_passes_test(lambda u: u.is_superuser)
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



from .models import Empresa, Dependencia  # Asegúrate de importar estos modelos

@login_required
@user_passes_test(lambda u: u.is_superuser)
def editar_empresa(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)
    if request.method == 'POST':
        form = EmpresaForm(request.POST, instance=empresa)
        if form.is_valid():
            form.save()
            return redirect('portada')
    else:
        form = EmpresaForm(instance=empresa)
    return render(request, 'editar_empresa.html', {'form': form})



@login_required
def registro_correspondencia(request, empresa_id):
    try:
        empresa = Empresa.objects.get(id=empresa_id)
        perfil = PerfilUsuario.objects.get(user=request.user)
        dependencias = perfil.dependencias.filter(empresa=empresa)
    except (Empresa.DoesNotExist, PerfilUsuario.DoesNotExist):
        return redirect('portada')

    if request.method == 'POST':
        form = CorrespondenciaForm(request.POST, request.FILES, user=request.user, empresa_id=empresa_id)
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

            return redirect('registro_correspondencia', empresa_id=empresa_id)
    else:
        form = CorrespondenciaForm(user=request.user, empresa_id=empresa_id)
        

    correspondencias = Correspondencia.objects.filter(dependencia__empresa=empresa).order_by('-fecha')

    return render(request, 'gestion/registro_correspondencia.html', {
        'form': form,
        'correspondencias': correspondencias,
        'empresa': empresa,
    })


# Vista para lista la correspondencia
@login_required
@user_passes_test(lambda u: u.is_superuser)

def lista_correspondencia(request):
    # Obtener todos los filtros del formulario GET
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    empresa_id = request.GET.get('empresa')
    dependencia_id = request.GET.get('dependencia')
    tipo_correspondencia = request.GET.get('tipo_correspondencia')
    adjuntos = request.GET.get('adjuntos')

    # Filtrar las correspondencias
    correspondencias = Correspondencia.objects.all()

    if fecha_inicio:
        correspondencias = correspondencias.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        correspondencias = correspondencias.filter(fecha__lte=fecha_fin)
    if empresa_id:
        correspondencias = correspondencias.filter(dependencia__empresa_id=empresa_id)
    if dependencia_id:
        correspondencias = correspondencias.filter(dependencia_id=dependencia_id)
    if tipo_correspondencia:
        correspondencias = correspondencias.filter(tipo_correspondencia=tipo_correspondencia)
    if adjuntos:
        correspondencias = correspondencias.exclude(documento="")

    # Crear el contexto de correspondencias con la URL del documento
    context = []
    for correspondencia in correspondencias:
        if correspondencia.documento:
            documento_url = correspondencia.documento.url
        else:
            documento_url = None
        
        context.append({
            'correspondencia': correspondencia,
            'documento_url': documento_url,
        })

    # Obtener todas las empresas y dependencias para los filtros
    empresas = Empresa.objects.all()
    dependencias = Dependencia.objects.all()

    # Retornar los datos filtrados y las empresas y dependencias para el formulario
    return render(request, 'lista_correspondencia.html', {
        'correspondencias': context,
        'empresas': empresas,
        'dependencias': dependencias,
    })


@login_required
@login_required
def responder_correspondencia(request, correspondencia_id):
    correspondencia = get_object_or_404(Correspondencia, id=correspondencia_id)

    if request.method == 'POST':
        form = RespuestaCorrespondenciaForm(request.POST, request.FILES, instance=correspondencia)
        if form.is_valid():
            form.save()
            messages.success(request, 'Respuesta guardada con éxito.')
            return redirect('registro_correspondencia', empresa_id=correspondencia.dependencia.empresa.id)  # Redirige a la lista de correspondencias
    else:
        form = RespuestaCorrespondenciaForm(instance=correspondencia)

    return render(request, 'gestion/responder_correspondencia.html', {
        'form': form,
        'correspondencia': correspondencia
    })




@login_required
def ver_respuesta(request, correspondencia_id):
    correspondencia = get_object_or_404(Correspondencia, id=correspondencia_id)

     # Obtener la empresa asociada a la dependencia de la correspondencia
    empresa = correspondencia.dependencia.empresa

    # Solo permitir ver la respuesta si la correspondencia ha sido respondida
    if not correspondencia.respondida:
        messages.error(request, "Esta correspondencia aún no ha sido respondida.")
        return redirect('registro_correspondencia', empresa_id=empresa.id)
    
    return render(request, 'gestion/ver_respuesta.html', {
        'correspondencia': correspondencia,
        'empresa': empresa  # Pasar la empresa al contexto
    })


# Vista del index (registro de correspondencia)
@login_required
def index(request):
    try:
        perfil_usuario = PerfilUsuario.objects.get(user=request.user)
        empresa = perfil_usuario.empresas.first()  # Cambiado a empresas.first()
    except PerfilUsuario.DoesNotExist:
        # Redirigir o mostrar un mensaje si no existe el perfil
        return render(request, 'gestion/error.html', {
            'mensaje': 'No se encontró el perfil del usuario.'
        })

    if request.method == 'POST':
        form = CorrespondenciaForm(request.POST, request.FILES, user=request.user, empresa_id=empresa.id if empresa else None)
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
        form = CorrespondenciaForm(user=request.user, empresa_id=empresa.id if empresa else None)

    correspondencias = Correspondencia.objects.filter(dependencia__empresa=empresa).order_by('-fecha') if empresa else Correspondencia.objects.none()

    return render(request, 'gestion/index.html', {
        'form': form,
        'correspondencias': correspondencias,
        'empresa': empresa
    })


# Vista para crear dependencias (solo admin)
@login_required
@user_passes_test(lambda u: u.is_superuser)
def crear_dependencia(request):
    if request.method == 'POST':
        form = DependenciaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('portada')  # Redirigir al index después de guardar la dependencia
    else:
        form = DependenciaForm()
    return render(request, 'gestion/crear_dependencia.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def editar_dependencia(request, dependencia_id):
    dependencia = get_object_or_404(Dependencia, id=dependencia_id)
    if request.method == 'POST':
        form = DependenciaForm(request.POST, instance=dependencia)
        if form.is_valid():
            form.save()
            return redirect('portada')
    else:
        form = DependenciaForm(instance=dependencia)
    return render(request, 'editar_dependencia.html', {'form': form})


# Vista para registrar usuario (solo admin)
@login_required
@user_passes_test(lambda u: u.is_superuser)
def registrar_usuario(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario creado exitosamente.")
            return redirect('portada')  # Redirigir a la página que prefieras después de crear el usuario
        else:
            messages.error(request, "Corrige los errores del formulario.")
            print(form.errors)  # Para depurar los errores en la consola
    else:
        form = RegistroUsuarioForm()

    return render(request, 'registro_usuario.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(User, pk=usuario_id)
    if request.method == 'POST':
        form = EditarUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('portada')  # Redirige a la portada o donde desees
    else:
        form = EditarUsuarioForm(instance=usuario)
    return render(request, 'editar_usuario.html', {'form': form})


@login_required
def adjuntar_documento(request, correspondencia_id):
    # Obtener la instancia de la correspondencia
    correspondencia = get_object_or_404(Correspondencia, id=correspondencia_id)

    # Obtener el empresa_id desde la dependencia de la correspondencia
    if correspondencia.dependencia and correspondencia.dependencia.empresa:
        empresa = correspondencia.dependencia.empresa  # Obtener la empresa relacionada
    else:
        messages.error(request, 'No se pudo determinar la empresa asociada a esta correspondencia.')
        return redirect('portada')  # Redirigir a la portada si no hay empresa asociada
    
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES, instance=correspondencia)

        if form.is_valid():
            # Guardar solo el documento subido
            form.save()
            messages.success(request, 'Documento adjuntado con éxito.')
            return redirect('registro_correspondencia', empresa_id=empresa.id)  # Redirigir con el empresa_id correcto
    else:
        form = DocumentoForm(instance=correspondencia)

    # Pasar la empresa al contexto
    return render(request, 'gestion/adjuntar_documento.html', {'form': form, 'correspondencia': correspondencia, 'empresa': empresa})




# Vista para cerrar sesión
def logout_view(request):
    logout(request)
    return redirect('login')  # Redirigir a la página de portada o la que prefieras después de cerrar sesión


@login_required
def filtrar_dependencias_por_empresa(request):
    empresas_ids = request.GET.getlist('empresas_ids[]')
    
    if empresas_ids:
        # Filtrar dependencias asociadas a la empresa seleccionada
        dependencias = Dependencia.objects.filter(empresa_id__in=empresas_ids).values('id', 'nombre', 'empresa__nombre')
        return JsonResponse(list(dependencias), safe=False)
    
    return JsonResponse([], safe=False)


# Vista para exportar a excel
@login_required
def exportar_excel(request):
    form = FiltroCorrespondenciaForm(request.GET, user=request.user)

    # Obtener las empresas y dependencias en función del usuario
    empresas = form.fields['empresa'].queryset
    dependencias = form.fields['dependencia'].queryset

    # Filtrar correspondencias
    correspondencias = Correspondencia.objects.all()

    if form.is_valid():
        # Aplicar filtros
        if form.cleaned_data['fecha_inicio']:
            correspondencias = correspondencias.filter(fecha__gte=form.cleaned_data['fecha_inicio'])
        if form.cleaned_data['fecha_fin']:
            correspondencias = correspondencias.filter(fecha__lte=form.cleaned_data['fecha_fin'])
        if form.cleaned_data['empresa']:
            correspondencias = correspondencias.filter(dependencia__empresa=form.cleaned_data['empresa'])
        if form.cleaned_data['dependencia']:
            correspondencias = correspondencias.filter(dependencia=form.cleaned_data['dependencia'])
        if form.cleaned_data['tipo_correspondencia']:
            correspondencias = correspondencias.filter(tipo_correspondencia=form.cleaned_data['tipo_correspondencia'])
        if form.cleaned_data['adjuntos']:
            correspondencias = correspondencias.exclude(documento="")

    # Verificar si la consulta tiene datos
    print(f"Correspondencias encontradas: {correspondencias.count()}")

    if correspondencias.exists():
        # Crear el archivo Excel
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Correspondencias"

        # Escribir los encabezados
        ws.append([
            "Consecutivo", "Tipo", "Dependencia", "Entrada/Salida", "Fecha", "Asunto", "Remitente", "Destinatario", "Necesita Respuesta", "Estado de Respuesta", "Documento", "Usuario Registró" 
        ])

        # Escribir los datos
        for correspondencia in correspondencias:
            ws.append([
                correspondencia.consecutivo,
                correspondencia.tipo_correspondencia,
                correspondencia.dependencia.nombre,
                correspondencia.entrada_salida,
                correspondencia.fecha,
                correspondencia.asunto,
                correspondencia.remitente,
                correspondencia.destinatario,
                "Sí" if correspondencia.necesita_respuesta else "No",
                "Respondida" if correspondencia.respondida else "Pendiente",
                "Sí" if correspondencia.documento else "No",
                correspondencia.user.username 
            ])

        # Crear la respuesta HTTP con el archivo Excel
        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = 'attachment; filename=correspondencias.xlsx'
        wb.save(response)
        
        return response
    else:
        messages.error(request, "No se encontraron correspondencias para exportar.")
        return redirect('lista_correspondencia')
    
    # Retornar la vista con los filtros
    return render(request, 'lista_correspondencia.html', {
        'form': form,
        'empresas': empresas,
        'dependencias': dependencias,
        'correspondencias': correspondencias,
    })



@login_required
@user_passes_test(lambda u: u.is_superuser)
def dashboard(request):
    # Filtrar y contar correspondencias
    correspondencias = Correspondencia.objects.all()
    total_correspondencias = correspondencias.count()
    
    # Agrupar por empresa
    correspondencias_por_empresa = correspondencias.values('dependencia__empresa__nombre').annotate(total=Count('id')).order_by('dependencia__empresa__nombre')
    
    # Preparar listas para etiquetas y datos
    empresas = [item['dependencia__empresa__nombre'] for item in correspondencias_por_empresa]
    totales = [item['total'] for item in correspondencias_por_empresa]

    # Datos de respondidas y pendientes
    respondidas = correspondencias.filter(respondida=True).count()
    pendientes = correspondencias.filter(respondida=False).count()

    # Filtrar correspondencias pendientes de respuesta
    correspondencias_pendientes = Correspondencia.objects.filter(necesita_respuesta=True, respondida=False).order_by('fecha_limite_respuesta')

    # Calcular días restantes y agregar al contexto
    for correspondencia in correspondencias_pendientes:
        if correspondencia.fecha_limite_respuesta:
            # Convertir fecha_limite_respuesta a solo fecha (si es datetime)
            fecha_limite = correspondencia.fecha_limite_respuesta.date() if isinstance(correspondencia.fecha_limite_respuesta, timezone.datetime) else correspondencia.fecha_limite_respuesta
            correspondencia.dias_restantes = (fecha_limite - timezone.now().date()).days
        else:
            correspondencia.dias_restantes = None

    return render(request, 'gestion/dashboard.html', {
        'total_correspondencias': total_correspondencias,
        'empresas': empresas,
        'totales': totales,
        'respondidas': respondidas,
        'pendientes': pendientes,
        'correspondencias_pendientes': correspondencias_pendientes,
    })


@login_required
def alertas_respuestas(request):
    correspondencias_pendientes = Correspondencia.objects.filter(
        necesita_respuesta=True,
        respondida=False,
        fecha_limite_respuesta__lte=timezone.now() + timedelta(days=3)  # Mostrar las que están por vencer en 3 días o menos
    )
    
    return render(request, 'gestion/alertas_respuestas.html', {'correspondencias': correspondencias_pendientes})

def error_view(request):
    return render(request, 'gestion/error.html', {"message": "Ha ocurrido un error"})


# Eliminar Usuario
@login_required
def eliminar_usuario(request, usuario_id):
    usuario = get_object_or_404(User, id=usuario_id)
    usuario.delete()
    return redirect('portada')

# Cambiar Contraseña
@login_required
def cambiar_contraseña_usuario(request, usuario_id):
    usuario = get_object_or_404(User, id=usuario_id)
    if request.method == 'POST':
        form = PasswordChangeForm(user=usuario, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect('portada')  # Ajusta según el nombre de la vista de portada
    else:
        form = PasswordChangeForm(user=usuario)
    return render(request, 'cambiar_contraseña.html', {'form': form, 'usuario': usuario})


@login_required
def editar_correspondencia(request, id):
    correspondencia = get_object_or_404(Correspondencia, id=id)
    if request.method == "POST":
        form = CorrespondenciaForm(request.POST, instance=correspondencia)
        if form.is_valid():
            form.save()
            return redirect('lista_correspondencia')  # Redirige a la lista de correspondencia
    else:
        form = CorrespondenciaForm(instance=correspondencia)
    return render(request, 'gestion/editar_correspondencia.html', {'form': form})

# Eliminar Correspondencia
@login_required
def eliminar_correspondencia(request, id):
    correspondencia = get_object_or_404(Correspondencia, id=id)
    correspondencia.delete()
    return redirect('lista_correspondencia')  # Redirige a la lista de correspondencia después de eliminar
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Correspondencia
from .forms import CorrespondenciaForm, DependenciaForm


def indice(request):
    # Suponiendo que el ID se pasa como un parámetro de la URL
    some_id = request.GET.get('id')  # Obtiene el ID de la URL

    # Verifica que se haya proporcionado un ID
    if some_id:
        try:
            # Intenta obtener el objeto de Correspondencia
            correspondencia = Correspondencia.objects.get(id=some_id)
        except Correspondencia.DoesNotExist:
            # Maneja el caso donde no se encuentra la correspondencia
            return HttpResponse("Correspondencia no encontrada", status=404)

        # Ahora puedes acceder a los atributos de correspondencia
        año = correspondencia.año  # Aquí accedes al año de la correspondencia

        # Resto de tu lógica aquí, como renderizar una plantilla
        return render(request, 'tu_template.html', {'correspondencia': correspondencia})

    # Si no se proporciona un ID, devuelve un error
    return HttpResponse("No se ha proporcionado un ID", status=400)



def index(request):
    # Si el método de la solicitud es POST, entonces es una nueva entrada
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
            nueva_correspondencia.usuario = request.user  # Usuario actual
            nueva_correspondencia.save()
            return redirect('index')
    else:
        form = CorrespondenciaForm()

    # Obtener toda la correspondencia registrada
    correspondencias = Correspondencia.objects.all()

    return render(request, 'gestion/index.html', {
        'form': form,
        'correspondencias': correspondencias
    })


def crear_dependencia(request):
    if request.method == 'POST':
        form = DependenciaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')  # Redirigir al index después de guardar la dependencia
    else:
        form = DependenciaForm()
    return render(request, 'gestion/crear_dependencia.html', {'form': form})
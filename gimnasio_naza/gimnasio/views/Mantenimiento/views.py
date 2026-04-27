from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from gimnasio.models import Mantenimiento, Elemento  # ← importar Elemento
from gimnasio.forms import MantenimientoForm
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@require_POST

def crear_elemento_ajax(request):
    from gimnasio.models import Categoria  # importa Categoria si es FK

    serial         = request.POST.get('serial')
    marca          = request.POST.get('marca')
    nombre_elemento = request.POST.get('nombre_elemento')
    peso_elemento  = request.POST.get('peso_elemento')
    estado         = request.POST.get('estado')
    fecha_ingreso  = request.POST.get('fecha_ingreso')
    categoria_id   = request.POST.get('categoria')
    imagen         = request.FILES.get('imagen')

    if not all([serial, marca, nombre_elemento, peso_elemento, estado, fecha_ingreso, categoria_id, imagen]):
        return JsonResponse({'error': 'Todos los campos son obligatorios'}, status=400)

    try:
        categoria = Categoria.objects.get(id=categoria_id)
    except Categoria.DoesNotExist:
        return JsonResponse({'error': 'Categoría no válida'}, status=400)

    elemento = Elemento.objects.create(
        serial=serial,
        marca=marca,
        nombre_elemento=nombre_elemento,
        peso_elemento=peso_elemento,
        estado=estado,
        fecha_ingreso=fecha_ingreso,
        categoria=categoria,
        imagen=imagen
    )

    return JsonResponse({
        'id': elemento.id,
        'nombre': elemento.nombre_elemento,
    })


# HISTORIAL DE MANTENIMIENTO
class MantenimientoListView(ListView):
    model = Mantenimiento
    template_name = 'mantenimiento/listar.html'
    context_object_name = 'mantenimientos'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["crear_url"] = reverse_lazy('gimnasio:crear_mantenimiento')
        return context


# REGISTRAR
class MantenimientoCreateView(CreateView):
    model = Mantenimiento
    form_class = MantenimientoForm
    template_name = 'mantenimiento/crear.html'
    success_url = reverse_lazy('gimnasio:listar_mantenimiento')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Crear Mantenimiento'
        return context 


# EDITAR
class MantenimientoUpdateView(UpdateView):
    model = Mantenimiento
    form_class = MantenimientoForm
    template_name = 'mantenimiento/crear.html'
    success_url = reverse_lazy('gimnasio:listar_mantenimiento')


# ELIMINAR
class MantenimientoDeleteView(DeleteView):
    model = Mantenimiento
    template_name = 'mantenimiento/eliminar.html'
    success_url = reverse_lazy('gimnasio:listar_mantenimiento')
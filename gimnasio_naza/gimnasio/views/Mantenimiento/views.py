from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from gimnasio.models import Mantenimiento, Elemento,Categoria  # ← importar Elemento y Categoria
from gimnasio.forms import MantenimientoForm
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import transaction
from django.utils import timezone
# Agrega esta vista a tu views.py de mantenimiento (o donde gestiones categorías)

@csrf_exempt
@require_POST
def crear_categoria_ajax(request):
    import json
    from gimnasio.models import Categoria

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'JSON inválido'}, status=400)

    nombre_categoria = data.get('nombre_categoria', '').strip()
    descripcion      = data.get('descripcion', '').strip()

    if not nombre_categoria or not descripcion:
        return JsonResponse({'error': 'Todos los campos son obligatorios'}, status=400)

    categoria = Categoria.objects.create(
        nombre_categoria=nombre_categoria,
        descripcion=descripcion
    )

    return JsonResponse({
        'id':     categoria.id,
        'nombre': categoria.get_nombre_categoria_display(),
    })
@csrf_exempt
@require_POST

def crear_elemento_ajax(request):
    try:
        with transaction.atomic():

            serial = request.POST.get('serial')
            marca = request.POST.get('marca')
            nombre = request.POST.get('nombre')
            peso = request.POST.get('peso')
            estado = request.POST.get('estado')
            cantidad = request.POST.get('cantidad')

            nombre_categoria = request.POST.get('nombre_categoria')
            descripcion = request.POST.get('descripcion_categoria')

            foto = request.FILES.get('foto')

            if not all([
                serial,
                marca,
                nombre,
                peso,
                estado,
                cantidad,
                nombre_categoria
            ]):
                return JsonResponse(
                    {'error': 'Todos los campos son obligatorios'},
                    status=400
                )

            categoria, creada = Categoria.objects.get_or_create(
                nombre_categoria=nombre_categoria,
                defaults={
                    'descripcion': descripcion
                }
            )

            elemento = Elemento.objects.create(
                serial=serial,
                marca=marca,
                nombre_elemento=nombre,
                peso_elemento=peso,
                estado=estado,
                nombre_categoria=categoria,
                cantidad=cantidad,
                imagen=foto,
                fecha_ingreso=timezone.now()
            )

            return JsonResponse({
                'id': elemento.id,
                'nombre': elemento.nombre_elemento,
                'categoria_id': categoria.id,
                'categoria_creada': creada
            })

    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)
    except Exception as e:
        print("Error al crear elemento:", str(e))
        return JsonResponse({'error': str(e)}, status=500)

# HISTORIAL DE MANTENIMIENTO
class MantenimientoListView(ListView):
    model = Mantenimiento
    template_name = 'Mantenimiento/listar.html'
    context_object_name = 'mantenimientos'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["crear_url"] = reverse_lazy('gimnasio:crear_mantenimiento')
        context['completados'] = Mantenimiento.objects.filter(estado='Completado').count()
        context['pendientes'] = Mantenimiento.objects.filter(estado='Pendiente').count()
        context['en_proceso'] = Mantenimiento.objects.filter(estado='En_Proceso').count()
        context['total_mantenimientos'] = Mantenimiento.objects.count() 
        return context


# REGISTRAR
class MantenimientoCreateView(CreateView):
    model = Mantenimiento
    form_class = MantenimientoForm
    template_name = 'Mantenimiento/crear.html'
    success_url = reverse_lazy('gimnasio:listar_mantenimiento')

    def get_initial(self):
        initial = super().get_initial()
        elemento_id = self.request.GET.get('elemento')
        if elemento_id:
            try:
                initial['elemento'] = Elemento.objects.get(pk=elemento_id)
            except Elemento.DoesNotExist:
                pass
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Crear Mantenimiento'
        elemento_id = self.request.GET.get('elemento')
        if elemento_id:
            context['elemento_pre'] = Elemento.objects.filter(pk=elemento_id).first()
        context['categorias'] = Categoria.objects.all()
        print("Categorías en contexto:", context['categorias'])
        return context
# EDITAR
class MantenimientoUpdateView(UpdateView):
    model = Mantenimiento
    form_class = MantenimientoForm
    template_name = 'Mantenimiento/crear.html'
    success_url = reverse_lazy('gimnasio:listar_mantenimiento')


# ELIMINAR
class MantenimientoDeleteView(DeleteView):
    model = Mantenimiento
    template_name = 'Mantenimiento/eliminar.html'
    success_url = reverse_lazy('gimnasio:listar_mantenimiento')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar Mantenimiento'
        return context
import json
from django.views import generic
from django.utils import timezone
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views.decorators.http import require_POST
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from gimnasio.models import *
from gimnasio.forms import ElementoForm
from django.db import IntegrityError
from django.contrib import messages

@require_POST
@csrf_exempt
def crear_nombre_categoria_ajax(request):
    try:

        data = json.loads(request.body)

        categoria = Categoria.objects.create(
            nombre_categoria=data['nombre_nombre_categoria'],
            descripcion=data['descripcion']
        )

        return JsonResponse({
            'success': True,
            'id': categoria.pk,
            'nombre': categoria.nombre_categoria
        })

    except IntegrityError:

        return JsonResponse({
            'success': False,
            'error': 'Ya existe una categoría con ese nombre.'
        }, status=400)

    except Exception as e:

        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


class ElementoListView(ListView):
    model = Elemento
    template_name = 'Elementos/listar.html'
    context_object_name = 'elementos'

    def get_queryset(self):
        qs = super().get_queryset()
        cat_id = self.request.GET.get('categoria')
        if cat_id:
            qs = qs.filter(nombre_categoria__id=cat_id)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Listado de Elementos'
        context['crear_url'] = reverse_lazy('gimnasio:crear_elemento')
        context['categorias'] = Categoria.objects.all()
        cat_id = self.request.GET.get('categoria')
        if cat_id:
            context['categoria_activa'] = Categoria.objects.filter(id=cat_id).first()
        else:
            context['categoria_activa'] = None
        return context
    
# ==============================
# LISTAR IMÁGENES DE ELEMENTOS
# ==============================

def listar_imagenes_elementos(request):
    imagenes = Elemento.objects.filter(imagen__isnull=False)
    return render(request, 'listar_elementos.html', {'imagenes': imagenes})


# ==============================
# REGISTRAR ELEMENTO
# ==============================

class ElementoCreateView(CreateView):
    model = Elemento
    form_class = ElementoForm
    template_name = 'Elementos/crear.html'
    success_url = reverse_lazy('gimnasio:listar_elementos')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Crear Elemento'
        context['list_url'] = reverse_lazy('gimnasio:listar_elementos')
        return context
    def form_valid(self, form):
        messages.success(
            self.request,
            "elemento creado correctamente"
        )
        return super().form_valid(form)

# ==============================
# MODIFICAR ELEMENTO
# ==============================

class ElementoUpdateView(UpdateView):
    model = Elemento
    form_class = ElementoForm
    template_name = 'Elementos/crear.html'
    success_url = reverse_lazy('gimnasio:listar_elementos')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Editar Elemento'
        context['list_url'] = reverse_lazy('gimnasio:listar_elementos')
        return context
    
    def form_valid(self, form):
        messages.success(
            self.request,
            "elemento editado correctamente "
        )
        return super().form_valid(form)


# ==============================
# ELIMINAR ELEMENTO
# ==============================

class ElementoDeleteView(DeleteView):
    model = Elemento
    template_name = 'Elementos/eliminar.html'
    success_url = reverse_lazy('gimnasio:listar_elementos')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar Elemento'
        context['list_url'] = reverse_lazy('gimnasio:listar_elementos')
        return context
    
    def form_valid(self, form):
        messages.success(
            self.request,
            "elemento eliminado  correctamente"
        )
        return super().form_valid(form)


# ==============================
# CREAR IMAGEN DE ELEMENTO
# ==============================

def crear_imagen_elemento(request):
    if request.method == 'POST':
        form = ElementoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('gimnasio:listar_elementos')
    else:
        form = ElementoForm()
    return render(request, 'crear_elemento.html', {'form': form})
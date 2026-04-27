import json
from django.views import generic
from django.utils import timezone
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from gimnasio.models import *
from gimnasio.forms import MembresiaForm
from django.http import HttpResponse,JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from datetime import date, datetime

def crear_usuario_ajax(request):

    if request.method != "POST":
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)

    
        if not data.get('documento') or not data.get('nombre') or not data.get('apellido') or not data.get('correo'):
            return JsonResponse({'error': 'Faltan campos obligatorios'})

  
        if Usuario.objects.filter(documento=data['documento']).exists():
            return JsonResponse({'error': 'El usuario ya existe'})

    
        if data.get('fecha_nacimiento'):
            fecha_nacimiento = datetime.strptime(data['fecha_nacimiento'], "%Y-%m-%d").date()
        else:
            fecha_nacimiento = date(2000, 1, 1)
        peso = float(data.get('peso') or 0)
        altura = float(data.get('altura') or 0)
        password = data.get('password') or "123456"
        user = User.objects.create(
            username=data['username'],
            email = data.get('correo','')
        )
        user.set_password(password)
        user.save()
        usuario = Usuario.objects.create(
            user=user,
            documento=data['documento'],
            nombre_usuario=data['nombre'],
            apellido_usuario=data['apellido'],
            correo_usuario=data['correo'],
            telefono_usuario=data.get('telefono', ''),
            fecha_nacimiento=fecha_nacimiento,
            peso_usuario=peso,
            altura_usuario=altura,
            genero_usuario=data.get('genero', 'M'),
            rol='cliente',
            estado='activo',
            fecha_registro=date.today()
        )
        membresia = Membresia.objects.create(
            fk_usuario = usuario
        )
        return JsonResponse({
            'id': usuario.id,
            'nombre': f"{usuario.nombre_usuario} {usuario.apellido_usuario}"
        })

    except Exception as e:
        return JsonResponse({
            'error': str(e)
        })
class MembresiaListView(ListView):
    model = Membresia
    template_name = 'Membresia/listar.html'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Listado de membresias'
        context['crear_url'] = reverse_lazy('gimnasio:crear_membresia')

        # // LOGICA PARA EL GRAFICO ///
        

        # Calculamos los estados
        activas = Membresia.objects.filter(estado='activo').count()
        vencidas = Membresia.objects.filter(estado='inactivo').count()

        context['total_membresias'] = activas + vencidas

        # Empaquetamos en JSON para Chart.js
        context['chart_labels'] = json.dumps(['Activas', 'Vencidas'])
        context['chart_data'] = json.dumps([activas, vencidas])

        return context


class MembresiaCreateView(CreateView):
    model = Membresia
    template_name = 'Membresia/crear.html'
    form_class = MembresiaForm
    success_url = reverse_lazy('gimnasio:listar_membresia')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Crear membresia'
        return context


class MembresiaUpdateView(UpdateView):
    model = Membresia
    template_name = 'Membresia/crear.html'
    success_url = reverse_lazy('gimnasio:listar_membresia')
    form_class = MembresiaForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Editar membresia'
        context['listar_url'] = reverse_lazy('gimnasio:listar_membresia')
        return context


class MembresiaDeleteView(DeleteView):
    model = Membresia
    template_name = 'Membresia/eliminar.html'
    success_url = reverse_lazy('gimnasio:listar_membresia')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar membresia'
        context['listar_url'] = reverse_lazy('gimnasio:listar_membresia')
        return context


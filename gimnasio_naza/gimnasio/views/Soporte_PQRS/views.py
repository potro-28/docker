from django.shortcuts import render, redirect
from django.http import HttpResponse,JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.db.models import Count
from gimnasio.models import *
from gimnasio.forms import Soporte_PQRSForm
import json
from django.http import HttpResponseRedirect

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

        usuario = Usuario.objects.create(
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

        return JsonResponse({
            'id': usuario.id,
            'nombre': f"{usuario.nombre_usuario} {usuario.apellido_usuario}"
        })

    except Exception as e:
        return JsonResponse({
            'error': str(e)
        })
#Listar Soporte_PQRS


# ===== REEMPLAZA ESTAS DOS VISTAS EN TU VIEWS.PY =====

class Soporte_PQRSListView(ListView):
    model = Soporte_PQRS
    template_name = 'Soporte_PQR/listar.html'
    
    def get_queryset(self):
        # 1. Obtenemos el objeto Usuario personalizado que corresponde al usuario autenticado (mono)
        # Si la relación en tu modelo Usuario hacia el User de Django se llama 'user', usamos fk_usuario__user.
        # Si se llama de otra forma, una opción 100% segura es traer primero el usuario de tu tabla:
        try:
            usuario_custom = Usuario.objects.get(user=self.request.user) # Ajusta 'user' si tu campo se llama 'fk_user' o similar
            return Soporte_PQRS.objects.filter(fk_usuario=usuario_custom)
        except Usuario.DoesNotExist:
            return Soporte_PQRS.objects.none() # Evita romper la vista si no se encuentra el perfil
    
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Listado de Soporte y PQRS'
        context['crear_url'] = reverse_lazy('gimnasio:crear_Soporte_PQRS')

        try:
            usuario_custom = Usuario.objects.get(user=self.request.user)
            context['total_peticion'] = Soporte_PQRS.objects.filter(fk_usuario=usuario_custom, tipo="peticion").count()
            context['total_queja'] = Soporte_PQRS.objects.filter(fk_usuario=usuario_custom, tipo="queja").count()
            context['total_reclamo'] = Soporte_PQRS.objects.filter(fk_usuario=usuario_custom, tipo="reclamo").count()
            context['total_sugerencia'] = Soporte_PQRS.objects.filter(fk_usuario=usuario_custom, tipo="sugerencia").count()
        except Usuario.DoesNotExist:
            context['total_peticion'] = context['total_queja'] = context['total_reclamo'] = context['total_sugerencia'] = 0

        return context


class Soporte_PQRSCreateView(CreateView):
    model = Soporte_PQRS
    template_name = 'Soporte_PQR/crear.html'
    form_class = Soporte_PQRSForm
    success_url = reverse_lazy('gimnasio:listar_Soporte_PQRS')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Crear Soporte y PQRS'
        context['listar_url'] = reverse_lazy('gimnasio:listar_Soporte_PQRS')
        return context
    
    def form_valid(self, form):
        from gimnasio.models import Usuario  # Ruta absoluta corregida
        
        try:
            # 1. Obtenemos el perfil de usuario del atleta logueado
            usuario_gym = Usuario.objects.get(user=self.request.user)
            
            # 2. Asignamos la relación y el estado al formulario (esto prepara el objeto)
            form.instance.fk_usuario = usuario_gym
            form.instance.estado = 'pendiente'
            
            # 3. Guardamos el formulario normalmente. 
            # Esto ejecutará internamente el proceso de guardado y la redirección
            messages.success(self.request, "Soporte guardado correctamente")
            return super().form_valid(form)
            
        except Usuario.DoesNotExist:
            form.add_error(None, "No se encontró un perfil de usuario asociado.")
            return self.form_invalid(form)

    def form_invalid(self, form):
        print("❌ EL FORMULARIO NO ES VÁLIDO POR ESTOS ERRORES:", form.errors)
        return super().form_invalid(form)

class Soporte_PQRSUpdateView(UpdateView):
    model = Soporte_PQRS
    form_class = Soporte_PQRSForm
    template_name = 'Soporte_PQR/crear.html'
    success_url = reverse_lazy('gimnasio:listar_Soporte_PQRS')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Editar Soporte y PQRS'
        context['listar_url'] = reverse_lazy('gimnasio:listar_Soporte_PQRS')
        return context
    
    def form_valid(self, form):
        messages.success(self.request, "Soporte editado correctamente")
        return super().form_valid(form)


# Eliminar Soporte_PQRS  
class Soporte_PQRSDeleteView(DeleteView):
    model = Soporte_PQRS
    template_name = 'Soporte_PQR/eliminar.html'
    success_url = reverse_lazy('gimnasio:listar_Soporte_PQRS')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar Soporte y PQRS'
        context['listar_url'] = reverse_lazy('gimnasio:listar_Soporte_PQRS')
        return context
    
    def form_valid(self, form):
        messages.success(self.request, "Soporte eliminado correctamente")
        return super().form_valid(form)
    


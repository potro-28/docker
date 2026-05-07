from django.shortcuts import render, redirect
import json
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.views.generic import CreateView, UpdateView, DeleteView,View
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from gimnasio.models import *
from gimnasio.forms import AsistenciaForm
from django.utils import timezone
from django.db import transaction

@csrf_exempt
def wizard_asistencia(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            user = User.objects.create_user(
                username=data['username'],
                password=data['password'],
                email=data['correo_usuario']
            )
            usuario = Usuario.objects.create(
                user=user,
                documento=data['documento'],
                nombre_usuario=data['nombre_usuario'],
                apellido_usuario=data['apellido_usuario'],
                correo_usuario=data['correo_usuario'],
                telefono_usuario=data['telefono_usuario'],
                fecha_nacimiento=data['fecha_nacimiento'],
                peso_usuario=data['peso_usuario'],
                altura_usuario=data['altura_usuario'],
                genero_usuario=data['genero_usuario'],
                rol='Cliente',
                estado='activo',
            )

            membresia = Membresia.objects.create(
                fk_usuario=usuario,
                fecha_inicio=data['fecha_inicio'],
                fecha_fin=data['fecha_fin'],
                estado=data['estado_membresia'],
            )

            return JsonResponse({
                'id': membresia.id,
                'nombre': f"{usuario.nombre_usuario} {usuario.apellido_usuario}"
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


# Listar asistencia ##
def crear_membresia_ajax(request):
    if request.method != "POST":
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)

        if not data.get('fecha_inicio') or not data.get('fecha_fin') or not data.get('estado'):
            return JsonResponse({'error': 'Faltan campos obligatorios'})


        fecha_inicio = datetime.strptime(data['fecha_inicio'], "%Y-%m-%d").date() \
            if data.get('fecha_inicio') else date(2000, 1, 1)

        membresia = Membresia.objects.create(                 
            fecha_inicio =data['fecha_inicio '],
            fecha_fin=data['fecha_fin'],
            estado=data['estado'],
            codigo_qr=data['codigo_qr']
        )

        return JsonResponse({
            'id': membresia.id,               
            'nombre': f"{membresia.nombre_usuario} {membresia.apellido_usuario}"
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def Listar_asistencia(request):
    nombre = {
        'titulo': 'Listado de Asistencias',
        'asistencias': Asistencia.objects.all()
    }
    return render(request, 'Asistencia/listar.html', nombre)


class AsistenciaListView(ListView):
    model = Asistencia
    template_name = 'Asistencia/listar.html'

    def dispatch(self, request, *args, **kwargs):
        # if request.method == 'GET':
            # return redirect('app:listar_categorias')
        return super().dispatch(request, *args, **kwargs)

    # metodo post

    # metodo context data
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Listado de asistencias'
        context['crear_url'] = reverse_lazy('gimnasio:crear_asistencia')
        return context


class AsistenciaCreateView(CreateView):
    model = Asistencia
    template_name = 'Asistencia/crear.html'
    form_class = AsistenciaForm
    success_url = reverse_lazy('gimnasio:listar_asistencia')
    # @method_decorator(csrf_exempt)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Crear asistencia'
        return context
    
class AsistenciaUpdateView(UpdateView):
    model = Asistencia
    template_name = 'Asistencia/crear.html'
    success_url = reverse_lazy('gimnasio:listar_asistencia')
    form_class = AsistenciaForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Editar Asistencia'
        context['listar_url'] = reverse_lazy('gimnasio:listar_asistencia')
        return super().get_context_data(**kwargs)

class AsistenciaDeleteView(DeleteView):
    model = Asistencia
    template_name = 'Asistencia/eliminar.html'
    success_url = reverse_lazy('gimnasio:listar_asistencia')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar Asistencia'
        context['listar_url'] = reverse_lazy('gimnasio:listar_asistencia')
        return context


def Qr(request):
    return render(request, 'Asistencia/listar.html')
class QR_register(View):
    def get(self, request):
        return render(request, 'Asistencia/listar.html')

    def post(self, request):
        try:
            data = json.loads(request.body)
            qr_code = data.get('codigo') 

            if not qr_code:
                return JsonResponse({'status': 400, 'mensaje': 'Código no enviado'}, status=400)
            try:
                membresia = Membresia.objects.filter(fk_usuario__documento=qr_code,estado='activo').first()
                if not membresia:
                    return JsonResponse({
                        'status': 404,
                        'mensaje': 'No se encontrp membresia activa para este usuario'
                    }, status=404)
                    
                hoy = date.today()
                if Asistencia.objects.filter(fk_membresia=membresia, fecha_asistencia=hoy).exists():
                    return JsonResponse({
                        'status': 409,
                        'mensaje': f'{membresia.fk_usuario.nombre_usuario} ya registro asistencia hoy'
                    })
                asistencia = Asistencia.objects.create(fk_membresia=membresia,fecha_asistencia=hoy,hora_ingreso=timezone.now().time())
                return JsonResponse({'status': 200,'mensaje': f'Asistencia registrada para {membresia.fk_usuario.nombre_usuario}'})
            
            except Exception as e:
                return JsonResponse({'status': 500, 'mensaje': f'Error: {str(e)}'}, status=500)
            
        except json.JSONDecodeError:
            return JsonResponse({'status': 400, 'mensaje': 'JSON inválido'}, status=400)
from django.shortcuts import render, redirect
from django.http import HttpResponse,JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.views.generic import CreateView , UpdateView , DeleteView
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from gimnasio.models import *
from gimnasio.forms import Masa_muscularForm
from django.contrib import messages
import json

@csrf_exempt
def crear_nutricion_ajax(request):
    import json

    data = json.loads(request.body)

    nutricion = Nutricion.objects.create(
        nivel_actividad=data['nivel_actividad'],
        tipo_objetivo=data['tipo_objetivo'],
        tipo_dieta=data['tipo_dieta'],
        fk_Usuario_id=data['fk_usuario']
    )

    return JsonResponse({
        'id': nutricion.id,
        'nombre': f" {nutricion.id} - {nutricion.fk_Usuario.nombre_usuario} - {nutricion.fk_Usuario.documento}"
    })

#Listar asistencia 
def Listar_masa_corporal(request):
    nombre ={
        'titulo':'Listado de Masa Muscular',
        'masa_muscular': Masa_corporal.objects.all()
    }
    return render(request,'Masa_muscular/listar.html', nombre)

class Masa_corporalListView(ListView):
    model = Masa_corporal
    template_name = 'masa_muscular/listar.html'
    # metodo dispatch
    #@method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        #if request.method == 'GET':
            #return redirect('app:listar_categorias')
        return super().dispatch(request, *args, **kwargs)
    
    # metodo post
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    #metodo context data 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Listado de masa corporal'
        context['crear_url'] = reverse_lazy('gimnasio:crear_masa_corporal')
        return context


class Masa_corporalCreateView(CreateView):
    model = Masa_corporal
    template_name = 'masa_muscular/crear.html'
    form_class = Masa_muscularForm
    success_url = reverse_lazy('gimnasio:listar_masa_corporal_clas')

    def form_valid(self, form):
        messages.success(self.request, "El registro de masa corporal se guardó correctamente.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Crear masa corporal'
        context['listar_url'] = reverse_lazy('gimnasio:listar_masa_corporal_clas')
        context['usuarios'] = Usuario.objects.all()
        return context
class Masa_corporalUpdateView(UpdateView):
    model = Masa_corporal
    template_name = 'Masa_muscular/crear.html'
    form_class = Masa_muscularForm
    success_url = reverse_lazy('gimnasio:listar_masa_corporal_clas')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Actualizar masa corporal'
        context['listar_url'] = reverse_lazy('gimnasio:listar_masa_corporal_clas')
        return context
class Masa_corporalDeleteView(DeleteView):
    model = Masa_corporal
    template_name = 'masa_muscular/eliminar.html'
    success_url = reverse_lazy('gimnasio:listar_masa_corporal_clas')
    #@method_decorator(csrf_exempt)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar masa corporal'
        context['listar_url'] = reverse_lazy('gimnasio:listar_masa_corporal_clas')
        return context
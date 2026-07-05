from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from gimnasio.models import Turnosentrenadores
from gimnasio.forms import TurnodeentrenadorForm
from django.contrib import messages

class TurnodeentrenadorListView(ListView):
    model = Turnosentrenadores
    template_name = 'turnodeentrenador/listar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Listado de turnos de entrenadores'
        context['crear_url'] = reverse_lazy('gimnasio:crear_turnodeentrenador')
        return context


class TurnodeentrenadorCreateView(CreateView):
    model = Turnosentrenadores
    form_class = TurnodeentrenadorForm
    template_name = 'turnodeentrenador/crear.html'
    success_url = reverse_lazy('gimnasio:listar_turnodeentrenador')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Crear Turno Entrenadores'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Registro de turno de entrenador creado correctamente')
        return super().form_valid(form)
    
class TurnodeentrenadorUpdateView(UpdateView):
    model = Turnosentrenadores
    form_class = TurnodeentrenadorForm
    template_name = 'turnodeentrenador/crear.html'
    success_url = reverse_lazy('gimnasio:listar_turnodeentrenador')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Editar Turno Entrenadores'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Turno de entrenador actualizado correctamente')
        return super().form_valid(form)
    
    def get_initial(self):
        initial = super().get_initial()

        if self.object.fecha_turno_inicio:
            initial['fecha_turno_inicio'] = self.object.fecha_turno_inicio.strftime('%Y-%m-%d')

        return initial
    
    def get_initial(self):
        initial = super().get_initial()

        if self.object.fecha_turno_final:
            initial['fecha_turno_final'] = self.object.fecha_turno_final.strftime('%Y-%m-%d')

        return initial

class TurnodeentrenadorDeleteView(DeleteView):
    model = Turnosentrenadores
    template_name = 'turnodeentrenador/eliminar.html'
    success_url = reverse_lazy('gimnasio:listar_turnodeentrenador')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar Turno Entrenadores'
        context['listar_url'] = reverse_lazy('gimnasio:listar_turnodeentrenador')
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Turno de entrenador eliminado correctamente')
        return super().form_valid(form)

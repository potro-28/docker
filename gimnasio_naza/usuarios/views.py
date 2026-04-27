from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from gimnasio.models import Usuario,Membresia,Asistencia
from datetime import date
# Create your views here.

from datetime import date

class DashboardUsuarioView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def obtener_dias_restantes(self, membresia):
        
        hoy = date(2026, 4, 15)
        if membresia.fecha_fin < hoy:
            return 0
        if membresia.fecha_inicio > hoy:
            return (membresia.fecha_fin - membresia.fecha_inicio).days
        return (membresia.fecha_fin - hoy).days

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        Usuario = self.request.user

        if hasattr(Usuario, 'usuario'):
            context['nombre_usuario'] = Usuario.usuario.nombre_usuario
            context['apellido_usuario'] = Usuario.usuario.apellido_usuario
            context['documento'] = Usuario.usuario.documento
            context['correo'] = Usuario.usuario.correo_usuario
            context['telefono'] = Usuario.usuario.telefono_usuario

            membresia = Membresia.objects.filter(
                fk_usuario=Usuario.usuario.id
            ).first()

            if membresia:
                dias_totales = (membresia.fecha_fin - membresia.fecha_inicio).days

                context['fecha_inicio'] = membresia.fecha_inicio
                context['fecha_fin'] = membresia.fecha_fin
                context['dias_restantes'] = self.obtener_dias_restantes(membresia)
                context['dias_totales'] = dias_totales
            else:
                context['fecha_inicio'] = None
                context['fecha_fin'] = None
                context['dias_restantes'] = None
                context['dias_totales'] = None

        return context
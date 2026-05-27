from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from gimnasio.models import Usuario,Membresia,Asistencia
from datetime import date,timedelta
import json
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

        usuario = self.request.user

        if hasattr(usuario, 'usuario'):

            context['nombre_usuario'] = usuario.usuario.nombre_usuario
            context['apellido_usuario'] = usuario.usuario.apellido_usuario
            context['documento'] = usuario.usuario.documento
            context['correo'] = usuario.usuario.correo_usuario
            context['telefono'] = usuario.usuario.telefono_usuario

            membresia = Membresia.objects.filter(
                fk_usuario=usuario.usuario,
                estado='activo'
            ).first()

            if membresia:

                asistencia = Asistencia.objects.filter(
                    fk_membresia=membresia
                )

                eventos = []

                fecha_actual = membresia.fecha_inicio

                while fecha_actual <= membresia.fecha_fin:

                    asistio = asistencia.filter(
                        fecha_asistencia=fecha_actual
                    ).exists()

                    if asistio:
                        color = 'green'
                        titulo = 'Asistió'
                    else:
                        color = 'red'
                        titulo = 'Faltó'

                    eventos.append({
                        'title': titulo,
                        'start': fecha_actual.strftime('%Y-%m-%d'),
                        'color': color
                    })

                    fecha_actual += timedelta(days=1)

                context['eventos'] = json.dumps(eventos)

                dias_totales = (
                    membresia.fecha_fin - membresia.fecha_inicio
                ).days

                context['fecha_inicio'] = membresia.fecha_inicio
                context['fecha_fin'] = membresia.fecha_fin
                context['dias_restantes'] = self.obtener_dias_restantes(membresia)
                context['dias_totales'] = dias_totales

            else:
                context['eventos'] = json.dumps([])
                context['fecha_inicio'] = None
                context['fecha_fin'] = None
                context['dias_restantes'] = None
                context['dias_totales'] = None

        return context
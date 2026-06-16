from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from gimnasio.models import Usuario,Membresia,Asistencia,Nutricion,Masa_corporal,Rutina,Certificacion_interna,Encuesta,Sancion,Soporte_PQRS
from datetime import date,timedelta
from django.views.generic import ListView
import json

from gimnasio.utilities.calcular_dias import calcular_dias
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
    

class MiNutricionView(LoginRequiredMixin, ListView):
    model = Nutricion
    template_name = "usuario/nutricion.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        if hasattr(usuario, 'usuario'):
            nutricion = Nutricion.objects.filter(fk_Usuario=usuario.usuario).first()
            
            context['nutricion'] = nutricion
        return context

class MiRutinaView(LoginRequiredMixin,ListView):
    model = Rutina
    template_name = "usuario/rutina.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        if hasattr(usuario,'usuario'):
            rutina = Rutina.objects.filter(fk_imc__fk_Nutricion__fk_Usuario = usuario.usuario)
            context['rutina'] = rutina
        return context
    

class MiCertificacionView(LoginRequiredMixin,ListView):
    model = Certificacion_interna
    template_name = "usuario/certificacion.html"
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        if hasattr(usuario,'usuario'):
            certificacion = Certificacion_interna.objects.filter(fk_membresia__fk_usuario = usuario.usuario)
            context['certificaciones'] = certificacion
        return context
    
class MiEncuestasView(LoginRequiredMixin,ListView):
    model = Encuesta
    template_name = 'usuario/encuestas.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        if hasattr(usuario,'usuario'):
            encuesta = Encuesta.objects.filter(
                miembros = usuario.usuario,
                estado = 'Activo'
            )
            context['encuesta'] = encuesta
        return context

class MisSancionesView(LoginRequiredMixin,ListView):
    model = Sancion
    template_name = 'usuario/sanciones.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        if hasattr(usuario,'usuario'):
            sancion = Sancion.objects.filter(fk_usuario = usuario.usuario)
            context['sancion'] = sancion
        return context


class MiPqrs(LoginRequiredMixin, ListView):
    model = Soporte_PQRS
    template_name = 'usuario/pqrs.html'
    context_object_name = 'lista_pqr'

    def get_queryset(self):
        return Soporte_PQRS.objects.filter(
            fk_usuario=self.request.user.usuario
        ).order_by('-fecha_ingreso', '-id')
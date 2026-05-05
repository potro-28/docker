import os
import re 
from django.forms import ModelForm, formset_factory, inlineformset_factory
from gimnasio.models import *
from django import forms
from datetime import date
from django.utils import timezone
from django.contrib.auth.models import User
from django.shortcuts import render
from django.db.models import Count
class ElementoForm(forms.ModelForm):
    class Meta:
        model = Elemento
        fields = '__all__'
        widgets = {
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date'}),
        }


    def clean(self):
        cleaned_data = super().clean()
        serial = cleaned_data.get('serial')
        nombre_elemento = cleaned_data.get('nombre_elemento')
        fecha_ingreso = cleaned_data.get('fecha_ingreso')
        
        if fecha_ingreso and fecha_ingreso > timezone.now().date():
            raise forms.ValidationError('La fecha de ingreso no puede ser futura.')

    
        qs = Elemento.objects.all()
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if serial and nombre_elemento and qs.filter(serial=serial,nombre_elemento=nombre_elemento).exists():
            raise forms.ValidationError('Ya existe un elemento con ese serial y nombre.')
        return cleaned_data
    def clean_serial(self):
        serial = self.cleaned_data.get('serial')
        if serial and not re.match(r'^[A-Z0-9]{5,10}$', serial):
            raise forms.ValidationError('El serial debe contener entre 5 y 10 caracteres alfanuméricos en mayúsculas.')
        return serial
    def clean_nombre_elemento(self):
        nombre_elemento = self.cleaned_data.get('nombre_elemento')
        if nombre_elemento and not re.match(r'^[a-zA-Z\s]+$', nombre_elemento):
            raise forms.ValidationError('El nombre del elemento solo puede contener letras y espacios.')
        return nombre_elemento
    def clean_fecha_ingreso(self):
        fecha_ingreso = self.cleaned_data.get('fecha_ingreso')
        if fecha_ingreso and fecha_ingreso > timezone.now().date():
            raise forms.ValidationError('La fecha de ingreso no puede ser futura.')
        return fecha_ingreso
    def clean_marca(self):
        marca = self.cleaned_data.get('marca')
        if marca:
            if marca != marca.strip():
                raise forms.ValidationError('La marca no puede contener espacios al inicio ni al final.')
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', marca):
            raise forms.ValidationError('La marca solo puede contener letras y espacios.')
        if '  ' in marca:
            raise forms.ValidationError('La marca no puede contener espacios consecutivos.')
        return marca
    def clean_imagen(self):
        imagen = self.cleaned_data.get('imagen')
        if imagen:
            ext = os.path.splitext(imagen.name)[1].lower()
            if ext != '.png' and ext != '.jpg' and ext != '.jpeg':
                raise forms.ValidationError('Solo se permiten imágenes en formato PNG, JPG o JPEG.')
        return imagen

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = '__all__'
        widgets = {
            'fecha_nacimiento': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),
            'peso_usuario': forms.NumberInput(
                attrs={'placeholder': 'kg'}
            ),
            'altura_usuario': forms.NumberInput(
                attrs={'placeholder': 'cm'}
            ),
        }
        exclude = ['user', 'estado', 'fecha_registro']

    def clean(self):
        cleaned_data = super().clean()
        documento        = cleaned_data.get('documento')
        nombre_usuario   = cleaned_data.get('nombre_usuario')
        apellido_usuario = cleaned_data.get('apellido_usuario')
        fecha_nacimiento = cleaned_data.get('fecha_nacimiento')
        telefono_usuario = cleaned_data.get('telefono_usuario')
        correo_usuario   = cleaned_data.get('correo_usuario')

        qs = Usuario.objects.all()
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if (documento and nombre_usuario and apellido_usuario and
                correo_usuario and telefono_usuario and fecha_nacimiento and
                qs.filter(
                    documento=documento,
                    nombre_usuario=nombre_usuario,
                    apellido_usuario=apellido_usuario,
                    correo_usuario=correo_usuario,
                    telefono_usuario=telefono_usuario,
                    fecha_nacimiento=fecha_nacimiento
                ).exists()):
            raise forms.ValidationError('Los datos de este usuario ya están registrados.')

        return cleaned_data

    def clean_documento(self):
        documento = self.cleaned_data.get('documento')
        if documento:
            if not re.match(r'^\d{7,10}$', documento):
                raise forms.ValidationError('El documento debe contener exactamente 7 a 10 dígitos numéricos.')
            for digito in set(documento):
                if documento.count(digito) > 5:
                    raise forms.ValidationError(
                        f'El documento no es válido: el dígito "{digito}" aparece más de 5 veces.'
                    )
        return documento

    def clean_nombre_usuario(self):
        nombre = self.cleaned_data.get('nombre_usuario')
        if not nombre:
            return nombre
        if nombre != nombre.strip():
            raise forms.ValidationError('El nombre no puede contener espacios al inicio ni al final.')
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombre):
            raise forms.ValidationError('El nombre solo puede contener letras y espacios.')
        if '  ' in nombre:
            raise forms.ValidationError('El nombre no puede contener espacios consecutivos.')
        return nombre

    def clean_apellido_usuario(self):
        apellido = self.cleaned_data.get('apellido_usuario')
        if not apellido:
            return apellido
        if apellido != apellido.strip():
            raise forms.ValidationError('El apellido no puede contener espacios al inicio ni al final.')
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', apellido):
            raise forms.ValidationError('El apellido solo puede contener letras y espacios.')
        if '  ' in apellido:
            raise forms.ValidationError('El apellido no puede contener espacios consecutivos.')
        return apellido

    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        if fecha_nacimiento is None:
            raise forms.ValidationError("Por favor ingresa una fecha de nacimiento.")
        hoy = date.today()
        if fecha_nacimiento >= hoy:
            raise forms.ValidationError("La fecha de nacimiento no puede ser hoy ni una fecha futura.")
        if fecha_nacimiento.year < 1900:
            raise forms.ValidationError("La fecha de nacimiento debe ser posterior al año 1900.")
        edad_minima = hoy.replace(year=hoy.year - 5)
        if fecha_nacimiento > edad_minima:
            raise forms.ValidationError("La fecha de nacimiento no es válida, verifica el año ingresado.")
        return fecha_nacimiento

    def clean_telefono_usuario(self):
        telefono = self.cleaned_data.get('telefono_usuario')
        if telefono:
            if not re.match(r'^3\d{9}$', telefono):
                raise forms.ValidationError('El teléfono debe contener exactamente 10 dígitos y comenzar con 3.')
        return telefono

    def clean_correo_usuario(self):
        correo = self.cleaned_data.get('correo_usuario')
        if not correo:
            return correo
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', correo):
            raise forms.ValidationError('Ingrese un correo electrónico válido.')
        if re.search(r'[^a-zA-Z0-9._%+\-@]', correo):
            raise forms.ValidationError('El correo solo puede contener letras, números y los caracteres especiales permitidos (. _ % + -).')
        return correo

    def clean_peso_usuario(self):
        peso = self.cleaned_data.get('peso_usuario')
        if peso is not None:
            if peso <= 0:
                raise forms.ValidationError('El peso debe ser un número positivo.')
            if peso < 30 or peso > 150:
                raise forms.ValidationError('El peso debe estar entre 30kg y 150kg.')
        return peso

    def clean_altura_usuario(self):
        altura = self.cleaned_data.get('altura_usuario')
        if altura is not None:
            if altura <= 0:
                raise forms.ValidationError('La altura debe ser un número positivo.')
            if altura < 100 or altura > 230:
                raise forms.ValidationError('La altura debe estar entre 100cm y 230cm.')
        return altura  
    
class MantenimientoForm(forms.ModelForm):
    class Meta:
        model = Mantenimiento
        fields = '__all__'
        widgets = {
            'fecha_programada': forms.DateInput(attrs={'type': 'date'}),
            'fecha_realizada': forms.DateInput(attrs={'type': 'date'}),
            'descripcion' : forms.TextInput(attrs={ 
                'class':'form-control',
                'placeholder': 'Ingrese la descripcion del mantenimiento'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha_programada = cleaned_data.get('fecha_programada')
        elemento = cleaned_data.get('Elemento')

        if elemento and fecha_programada:
            qs = Mantenimiento.objects.filter(Elemento=elemento)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.filter(fecha_programada=fecha_programada).exists():
                raise forms.ValidationError('Ya existe un mantenimiento programado para esa fecha en este elemento.')

        return cleaned_data
    
    
class AsistenciaForm(forms.ModelForm):
                
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_asistencia'].initial = datetime.now().date()
        self.fields['hora_ingreso'].initial = datetime.now().strftime('%H:%M') 
    class Meta:
 
        model = Asistencia
        fields = '__all__'
        widgets = {
            'hora_ingreso': forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time',
            'value': datetime.now().strftime('%H:%M'),
            }),
            'fecha_asistencia': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'value': datetime.now().strftime('%d-%m-%Y'),     
            }),        
        }
    def clean(self):
        cleaned_data = super().clean()
        fecha_asistencia = cleaned_data.get('fecha_asistencia')
        fk_membresia = cleaned_data.get('fk_membresia')
       
    
        if fecha_asistencia > forms.fields.datetime.date.today():
            self.add_error('fecha_asistencia','La fecha de asistencia no puede ser futura')
        if fecha_asistencia < forms.fields.datetime.date.today():
            self.add_error('fecha_asistencia','La fecha de asistencia no puede ser anterior al día de hoy')
        

        asistencia_existente = Asistencia.objects.filter(fk_membresia__fk_usuario=fk_membresia.fk_usuario, fecha_asistencia=fecha_asistencia)

        if asistencia_existente.exists():
            self.add_error('fk_membresia', f'Ya existe una asistencia registrada para este usuario el día de hoy')

        


class MembresiaForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_inicio'].initial = datetime.now().date()
       
    class Meta:
        model = Membresia
        fields = '__all__'
        widgets = {
            
            'fecha_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'value': datetime.now().strftime('%d-%m-%Y'),     
            }),  
                'fecha_fin': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'value': datetime.now().strftime('%d-%m-%Y'),     
            }),  
        }
        
    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        fk_usuario = cleaned_data.get('fk_usuario')
        
        if fecha_inicio > forms.fields.datetime.date.today():
            self.add_error('fecha_inicio','La fecha de inicio no puede ser futura')
        if fecha_inicio < forms.fields.datetime.date.today():
           self.add_error('fecha_inicio','La fecha de inicio no puede ser anterior al día de hoy')
        if fecha_fin > forms.fields.datetime.date.today() + forms.fields.datetime.timedelta(days=30):
            self.add_error('fecha_fin','La fecha de finalización no puede ser mayor a un mes')
        if fecha_fin < forms.fields.datetime.date.today() + forms.fields.datetime.timedelta(days=30):
            self.add_error('fecha_fin','La fecha de finalización no puede ser menor a un mes')
        if fecha_fin < forms.fields.datetime.date.today():
            self.add_error('fecha_fin','La fecha de finalización no puede ser anterior al día de hoy')
        if fecha_fin == fecha_inicio:
            self.add_error('fecha_fin','La fecha de finalización no puede ser igual a la fecha de inicio')
        if fecha_fin < fecha_inicio:
            self.add_error('fecha_fin','La fecha de finalización no puede ser anterior a la fecha de inicio')
        if fk_usuario and Membresia.objects.filter(fk_usuario=fk_usuario, fecha_inicio__month=fecha_inicio.month).exists():
            raise forms.ValidationError('El usuario ya tuvo una membresia este mismo mes')
        return cleaned_data
    
    

class NotificacionForm(forms.ModelForm):
    class Meta:
        model = Notificacion
        fields = '__all__'
        widgets ={
            'fk_usuario': forms.Select(attrs={'class': 'form-control'}),
            
            'tipo_notificacion': forms.Select(attrs={
                'class': 'form-control',
            }),
            'canal_notificacion': forms.Select(attrs={
                'class': 'form-control',
            }),
            'fk_membresia': forms.Select(attrs={
                'class': 'form-control',
            }),
            'fk_asistencia': forms.Select(attrs={
                'class': 'form-control',
            }),
            'fk_mantenimiento': forms.Select(attrs={
                'class': 'form-control',
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_notificacion = cleaned_data.get('tipo_notificacion')
        canal_notificacion = cleaned_data.get('canal_notificacion')
        exist_notificacion = Notificacion.objects.filter(tipo_notificacion=tipo_notificacion).exclude(pk=self.instance.pk).exists()
        exit_canal = Notificacion.objects.filter(canal_notificacion=canal_notificacion).exclude(pk=self.instance.pk).exists()
        if exist_notificacion and exit_canal:
            self.add_error('tipo_notificacion', 'Ya existe una notificación con este tipo y canal')
        return cleaned_data
        
        
        



class EncuestaForm(forms.ModelForm):
    miembros = forms.ModelMultipleChoiceField(
        queryset=Usuario.objects.filter(estado='activo'),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=False,
        label="Seleccionar Miembros"
    )
    
    class Meta:
        model = Encuesta
        fields = ['nombre', 'estado', 'fk_usuario', 'miembros']
        widgets = {
            'nombre' : forms.TextInput(attrs={ 
                'class':'form-control',
                'placeholder': 'Ingrese el nombre de la encuesta'}),
            
            'estado':
                forms.Select(attrs={
                'class':'form-control'}),
            'fk_usuario':
                forms.Select(attrs={
                    'class':'form-control',
                })      
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if not nombre:
            raise forms.ValidationError("El nombre es obligatorio")

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombre):
            raise forms.ValidationError(
                'El nombre solo puede contener letras'
            )
        existe = Encuesta.objects.filter(nombre=nombre)

        if self.instance.pk:
            existe = existe.exclude(pk=self.instance.pk)
        if existe.exists():
            raise forms.ValidationError(
                'Ya existe una encuesta con ese nombre'
            )
        return nombre

class PreguntaForm(forms.ModelForm):
    opciones = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Opciones separadas por comas (para opciones múltiples)',
            'rows': 3
        })
    )

    class Meta:
        model = Pregunta
        fields = ['pregunta', 'tipo', 'opciones', 'requerida']
        widgets = {
            'pregunta': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la pregunta'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'requerida': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    # forms.py
    def clean_opciones(self):
        opciones = self.cleaned_data.get('opciones')
        tipo = self.cleaned_data.get('tipo')
        # Validar que si es opción múltiple, existan opciones
        if tipo in ['multiple_choice', 'check_boxes', 'dropdown'] and not opciones:
            raise forms.ValidationError("Debe proporcionar opciones para este tipo de pregunta")
        if opciones:
            # Convierte el texto "1,2" en una lista de Python ['1', '2'] para el JSONField
            return [op.strip() for op in opciones.split(',') if op.strip()]
        return None

PreguntaFormSet = inlineformset_factory(
    Encuesta, 
    Pregunta, 
    form=PreguntaForm, 
    extra=1,        # ✅ Solo 1 pregunta inicial
    can_delete=True,
    max_num=20,     # ✅ Permite hasta 20 preguntas
    validate_max=False
)

class Soporte_PQRSForm(ModelForm):
    class Meta:
        model = Soporte_PQRS
        fields = '__all__'
        widgets = {
            'tipo' : forms.Select(attrs={ 
            'class':'form-control',
            'placeholder': 'Ingrese el tipo de soporte pqr'}),
            'descripcion' : forms.TextInput(attrs={ 
            'class':'form-control',
                
                'placeholder': 'Ingrese la descripcion del soporte pqr'}),
            'fecha_ingreso': forms.DateInput(attrs={ 
                'class': 'form-control',
                'type': 'date'
            }),
            'estado':
                forms.Select(attrs={
                'class':'form-control',  
                'placeholder': 'Ingrese el estado del soporte pqr',
                'rows':3,
                'cols':3}),
            'fk_usuario':
                forms.Select(attrs={
                    'class':'form-control',
                })      
        }
    
    def clean_descripcion(self):
        descripcion = self.cleaned_data['descripcion']

        if len(descripcion) < 10:
            raise forms.ValidationError("La descripción debe tener mínimo 10 caracteres")
        if len(descripcion) > 200:
            raise forms.ValidationError("La descripcion  no debe tener mas de 200 caracteres")

        return descripcion
    
    def clean_fecha_ingreso(self):
        fecha_ingreso = self.cleaned_data['fecha_ingreso']
        if fecha_ingreso < date.today():
            raise forms.ValidationError('La fecha de ingreso no puede ser anterior a la de hoy')
        return fecha_ingreso
        
class Reportes_estadisticasForm(forms.ModelForm):
    class Meta:
        model = Reportes_estadisticas
        fields = '__all__'
        widgets = {
            'tipo_reporte': forms.Select(attrs={ 
                'class': 'form-control',
            }),
            'descripcion' : forms.TextInput(attrs={ 
                'class':'form-control',
                
                'placeholder': 'Ingrese la descripcion del reporte o estadistica'}),
            'fecha_generacion': forms.DateInput(attrs={ 
                'class': 'form-control',
                'type': 'date'
            }),
            'formato':
                forms.Select(attrs={
                'class':'form-control',  
                'placeholder': 'Ingrese el formato del reporte',
                'rows':3,
                'cols':3}),
            'fk_usuario':
                forms.Select(attrs={
                    'class':'form-control',
                })      
        }
    
    def clean_fecha_generacion(self):
        fecha_generacion = self.cleaned_data.get('fecha_generacion')
        if fecha_generacion > date.today():
            raise forms.ValidationError("La fecha no puede ser futura.")
        if fecha_generacion < date(2025, 1, 1):
            raise forms.ValidationError("La fecha no puede ser anterior al 1 de enero de 2025.")
        return fecha_generacion
    
    def clean_descripcion(self):
        descripcion = self.cleaned_data['descripcion']

        if len(descripcion) < 10:
            raise forms.ValidationError("La descripción debe tener mínimo 10 caracteres")
        if len(descripcion) > 200:
            raise forms.ValidationError("La descripcion  no debe tener mas de 200 caracteres")

        return descripcion
        
class CategoriaForm(forms.ModelForm):

    class Meta:
        model = Categoria
        fields = '__all__'

        widgets = {
            'nombre_categoria': forms.Select(attrs={
                'class': 'form-control'
            }),

            'descripcion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese la descripción'
            }),
        }

    def clean_nombre_categoria(self):
        nombre = self.cleaned_data.get('nombre_categoria')
        if nombre and not nombre.isalpha():
            raise forms.ValidationError("El Nombre no puede contener números")
        return nombre

    def clean_material(self):
        material = self.cleaned_data.get('material')
        if material and not material.isalpha():
            raise forms.ValidationError("El Material no puede contener números")
        return material

    def clean_peso_equipo(self):
        peso = self.cleaned_data.get('peso_equipo')
        if peso and not str(peso).isdigit():
            raise forms.ValidationError("El Peso_Equipo solo puede contener números")
        return peso

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')
        if descripcion:
            if len(descripcion) < 10:
                raise forms.ValidationError("La descripción debe tener al menos 10 caracteres")
            if len(descripcion) > 250:
                raise forms.ValidationError("La descripción no puede tener más de 250 caracteres")
        return descripcion
    
    
    


    
class NutricionForm(forms.ModelForm):
    class Meta:
        model = Nutricion
        fields = '__all__'
        widgets = {
            'nombre' : forms.TextInput(attrs={
                'placeholder': 'Ingrese el nombre de la nutricion'}),
            
        }
        

class RutinaForm(ModelForm):
    class Meta:
        model = Rutina
        fields = '__all__'
        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'form-control'
            }),
            'dias_disponibles': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 7
            }),
        }

    def clean_dias_disponibles(self):
        dias_disponibles = self.cleaned_data.get('dias_disponibles')
        if dias_disponibles < 1 or dias_disponibles > 7:
            raise forms.ValidationError("Los días disponibles deben estar entre 1 y 7.")
        return dias_disponibles

class Masa_muscularForm(ModelForm):
    class Meta:
        model = Masa_corporal
        fields = '__all__'
        widgets = {
            'fecha_control': forms.DateInput(attrs={
                'type': 'date'
            }),
        }

    def clean_peso_cliente(self):
        peso = self.cleaned_data.get('peso_cliente')

        if peso <= 0:
            raise forms.ValidationError("El peso debe ser mayor que 0.")

        if peso < 30 or peso > 300:
            raise forms.ValidationError("El peso debe estar entre 30kg y 300kg.")

        return peso

    def clean_altura_cliente(self):
        altura = self.cleaned_data.get('altura_cliente')

        if altura <= 0:
            raise forms.ValidationError("La altura debe ser mayor que 0.")

        if altura < 0.5 or altura > 2.5:
            raise forms.ValidationError("La altura debe estar entre 0.5m y 2.5m.")

        return altura

    def clean_fecha_control(self):
        fecha = self.cleaned_data.get('fecha_control')
        if fecha > date.today():
            raise forms.ValidationError("La fecha no puede ser futura.")
        if fecha < date(1950, 1, 1):
            raise forms.ValidationError("La fecha no puede ser anterior al 1 de enero de 1950.")
        return fecha

    def clean(self):
        cleaned_data = super().clean()
        fk_nutricion = cleaned_data.get('fk_Nutricion')
        fecha = cleaned_data.get('fecha_control')

        if fk_nutricion and fecha:
            queryset = Masa_corporal.objects.filter(
                fk_Nutricion=fk_nutricion,
                fecha_control=fecha
            )

            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise forms.ValidationError(
                    "Ya existe un control para esta nutrición en esa fecha."
                )

        return cleaned_data

class SancionesForm(forms.ModelForm):
    class Meta:
        model = Sancion
        fields = '__all__'
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_motivo_sancion(self):
        motivo = self.cleaned_data.get('motivo_sancion')

        if not motivo or len(motivo.strip()) < 5:
            raise forms.ValidationError("El motivo debe tener al menos 5 caracteres.")

        motivo = motivo.strip()

        if not motivo[0].isalpha():
            raise forms.ValidationError("La descripción debe iniciar obligatoriamente con una letra.")

        return motivo

    def clean_duracion_sancion(self):
        duracion = self.cleaned_data.get('duracion_sancion')

        if duracion <= 0:
            raise forms.ValidationError("La duración debe ser mayor que 0 días.")

        if duracion > 365:
            raise forms.ValidationError("La duración no puede ser mayor a 365 días.")

        return duracion

    def clean(self):
        cleaned_data = super().clean()

        duracion = cleaned_data.get('duracion_sancion')
        usuario = cleaned_data.get('fk_usuario')
        tipo = cleaned_data.get('tipo_sancion')
        estado = cleaned_data.get('estado')

        fecha_inicio = date.today()
        cleaned_data['fecha_inicio'] = fecha_inicio

        if duracion:
            fecha_fin = fecha_inicio + timedelta(days=duracion)
            cleaned_data['fecha_fin'] = fecha_fin

        if usuario and tipo and estado == 'activa':
            queryset = Sancion.objects.filter(
                fk_usuario=usuario,
                tipo_sancion=tipo,
                estado='activa'
            )

            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise forms.ValidationError(
                    "Este usuario ya tiene una sanción activa de este tipo."
                )

        return cleaned_data

    def clean(self):
        cleaned_data = super().clean()

        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        usuario = cleaned_data.get('fk_usuario')
        tipo = cleaned_data.get('tipo_sancion')
        estado = cleaned_data.get('estado')

        if fecha_inicio and fecha_fin:
            if fecha_fin <= fecha_inicio:
                raise forms.ValidationError(
                    "La fecha de fin debe ser mayor que la fecha de inicio."
                )

        if usuario and tipo and estado == 'activa':
            queryset = Sancion.objects.filter(
                fk_usuario=usuario,
                tipo_sancion=tipo,
                estado='activa'
            )

            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise forms.ValidationError(
                    "Este usuario ya tiene una sanción activa de este tipo."
                )

        return cleaned_data


class RegistrovisitantetemporalForm(ModelForm):
    class Meta:
        model = Registrovisitantestemporales
        fields = '__all__'
        widgets = {
            'fecha_registro': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fk_usuario': forms.Select(attrs={
                'class': 'form-control',
            }),
        }
    def clean_fecha_registro(self):
        fecha_registro = self.cleaned_data.get('fecha_registro')
        hoy = timezone.now().date()
        if fecha_registro < hoy:
            raise forms.ValidationError(
            "La fecha de registro no puede ser en el pasado."
        )
        if fecha_registro > hoy:
            raise forms.ValidationError(
            "La fecha de registro no puede ser en el futuro."
        )
        return fecha_registro
    
class TurnodeentrenadorForm(ModelForm):
    administrador = forms.ModelChoiceField(
        queryset=Usuario.objects.filter(rol='Admin'),
        empty_label="Seleccione un administrador",
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Administrador",
        required=True
    )

    class Meta:
        model = Turnosentrenadores
        fields = [
            'administrador',         
            'fecha_turno_inicio',
            'fecha_turno_final',
            'jornada',
        ]
        widgets = {
            'fecha_turno_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_turno_final': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'jornada': forms.Select(attrs={
                'class': 'form-control',
            }),
        }

    def clean_fecha_turno_inicio(self):
        inicio = self.cleaned_data.get('fecha_turno_inicio')
        hoy = timezone.now().date()

        if inicio and inicio < hoy:
            raise forms.ValidationError(
                "La fecha de inicio no puede ser en el pasado."
            )
        return inicio

    def clean_fecha_turno_final(self):
        fin = self.cleaned_data.get('fecha_turno_final')
        hoy = timezone.now().date()

        if fin and fin < hoy:
            raise forms.ValidationError(
                "La fecha de finalización no puede ser en el pasado."
            )
        return fin

    def clean(self):
        cleaned_data = super().clean()
        inicio = cleaned_data.get('fecha_turno_inicio')
        fin = cleaned_data.get('fecha_turno_final')

        if inicio and fin and fin < inicio:
            self.add_error(
                'fecha_turno_final',
                "La fecha final no puede ser menor a la fecha de inicio."
            )

        return cleaned_data
class CertificacioninternaForm(ModelForm):
    class Meta:
        model = Certificacion_interna
        fields = '__all__'
        widgets = {
            'fecha_certificacion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'descripcion_certificacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese la descripcion de la certificacion interna'
            }),
            'fk_membresia': forms.Select(attrs={
                'class': 'form-control',
            }),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filtrar membresías con mínimo 10 asistencias
        membresias_validas = Membresia.objects.annotate(
            total_asistencias=Count('asistencia')
        ).filter(total_asistencias__gte=1)

        self.fields['fk_membresia'].queryset = membresias_validas
    def clean_descripcion_certificacion(self):
        descripcion_certificacion = self.cleaned_data['descripcion_certificacion']
        if len(descripcion_certificacion) < 10:
            raise forms.ValidationError("La descripcion de la certificacion interna debe tener al menos 10 caracteres.")
        if descripcion_certificacion.isdigit():
            raise forms.ValidationError("La descripcion de la certificacion interna no puede ser solo números.")
        if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ]', descripcion_certificacion):
            raise forms.ValidationError(
                "La descripción debe comenzar con una letra."
            )        
        return descripcion_certificacion
    
    def clean_fecha_certificacion(self):
        fecha_certificacion = self.cleaned_data['fecha_certificacion']
        hoy = timezone.now().date()
        if fecha_certificacion < hoy:
            raise forms.ValidationError(
            "La fecha de certificación no puede ser una fecha pasada."
        )
        if fecha_certificacion > hoy:
            raise forms.ValidationError(
            "La fecha de certificación no puede ser una fecha futura."
        )
        return fecha_certificacion    

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    
    class Meta:
        model = User
        fields = ['username','password']
        


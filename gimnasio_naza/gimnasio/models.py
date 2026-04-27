from django.db import models
from datetime import *
from decimal import Decimal  
from django.contrib.auth.models import User
import qrcode
from io import BytesIO
from django.core.files import File
# Create your models here.
#---------------------------------MODELO USUARIO-----------------------------------------       

class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='usuario')
    documento = models.CharField(max_length=45, unique=True)
    nombre_usuario = models.CharField(max_length=45)
    apellido_usuario = models.CharField(max_length=45)
    fecha_nacimiento = models.DateField()
    telefono_usuario = models.CharField(max_length=45)
    correo_usuario = models.CharField(max_length=100, unique=True)
    peso_usuario = models.DecimalField(max_digits=10, decimal_places=2)
    altura_usuario = models.DecimalField(max_digits=10, decimal_places=2)
    genero_usuario = models.CharField(max_length=10, choices=[('M', 'Masculino'), ('F', 'Femenino')], default='M')
    foto = models.ImageField(upload_to='usuarios/', null=True, blank=True)

    ROL_CHOICES = [
        ('Cliente', 'Cliente'),
        ('Administrador', 'Administrador'),
    ]
    rol = models.CharField(max_length=30, choices=ROL_CHOICES,null=True, blank=True)

    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('visitante', 'Visitante'),
    ]
    estado = models.CharField(max_length=30, choices=ESTADO_CHOICES)
    fecha_registro = models.DateField()

    def __str__(self):
        return str(self.documento)+("/")+(self.nombre_usuario) 

    fecha_registro = models.DateField(default=datetime.now)
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        db_table = 'usuario'
    def __str__(self):
        return self.user.username
    
#-----------------------------MODELO MEMBRESIA---------------------------------------------------
class Membresia(models.Model):
    
    fecha_inicio = models.DateField(default=datetime.now, verbose_name='Fecha de Inicio')
    fecha_fin = models.DateField(null=True, blank=True, verbose_name='Fecha de Finalizacion')
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]
    estado = models.CharField(max_length=30, choices=ESTADO_CHOICES)
    qr_code = models.ImageField(upload_to='qrs_membresias/', blank=True, null=True)
    fk_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)


    def save(self, *args, **kwargs):
        datos_qr = self.fk_usuario.documento 
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(datos_qr)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        
        nombre_archivo = f'qr_{datos_qr}.png'
        self.qr_code.save(f'qr_{nombre_archivo}.png', File(buffer), save=False)
        super().save(*args, **kwargs)
    
    @property
    def es_valida(self):
        return self.esta_activa and self.fecha_vencimiento >= timezone.now().date()
    
    def __str__(self):
        return str(self.fk_usuario.documento)+ ("/")+(self.fk_usuario.nombre_usuario)

    class Meta:
        verbose_name = 'Membresia'
        verbose_name_plural = 'Membresias'
        db_table = 'membresia'


#---------MODELO ASISTENCIA -----------------------------------------------------
class Asistencia(models.Model):
    fecha_asistencia = models.DateField(default=date.today, verbose_name='Fecha de Asistencia')
    hora_ingreso = models.TimeField(null=True, blank=True, verbose_name='Hora de Ingreso')
    fk_membresia = models.ForeignKey(Membresia, on_delete=models.CASCADE)


    def __str__(self):
        return str(f"{self.id}-{self.fecha_asistencia}/{self.fk_membresia.fk_usuario.nombre_usuario}")

    class Meta:
        verbose_name = 'Asistencia'
        verbose_name_plural = 'Asistencias'
        db_table = 'asistencia'

#--------------------CATEGORIA------------------
class Categoria(models.Model):

    NOMBRE_CATEGORIA = [
        ('maquinas', 'Máquinas'),
        ('mancuernas', 'Mancuernas'),
        ('discos', 'Discos'),
        ('accesorios', 'Accesorios'),
        ('barras', 'Barras'),
    ]
    

    nombre_categoria = models.CharField(max_length=45, choices=NOMBRE_CATEGORIA)
    descripcion = models.CharField(max_length=250)

    def __str__(self):
        return str(self.nombre_categoria)

    class Meta:
        db_table = "Categoria"
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

        

class Elemento(models.Model):
    serial = models.CharField(max_length=45, unique=True)
    marca = models.CharField(max_length=45)
    nombre_elemento = models.CharField(max_length=45)

    TIPO_CHOICES = [
        ('maquina', 'Máquina'),
        ('disco', 'Disco'),
        ('mancuerna', 'Mancuerna'),
        ('barra', 'Barras'),
        ('otro', 'Otro'),
    ]

    peso_elemento = models.DecimalField(max_digits=10, decimal_places=2)

    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]

    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    fecha_ingreso = models.DateField()
    categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE)

    cantidad = models.IntegerField(default=1)  # ✅ agregado
    imagen = models.ImageField(upload_to='elementos/', null=True, blank=True)

    def __str__(self):
        return self.nombre_elemento


class Mantenimiento(models.Model):
    fecha_programada = models.DateField()

    TIPO_CHOICES = [
        ('preventivo', 'Preventivo'),
        ('correctivo', 'Correctivo'),
    ]
    tipo_mantenimiento = models.CharField(max_length=20, choices=TIPO_CHOICES)

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En proceso'),
        ('completado', 'Completado'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES)

    nombre_elemento = models.ForeignKey(Elemento, on_delete=models.CASCADE)
    descripcion = models.TextField()

    def __str__(self):
        return str(self.id) 
#---------------------------------MODELO NOTIFCACIONES-----------------------------------------
TIPO_NOTIFICACION = [
    ('MEMBRESIA', 'Membresía'),
    ('MANTENIMIENTO', 'Mantenimiento'),
    ('ASISTENCIA', 'Asistencia'),
]

CANAL_NOTIFICACION = [
    ('SMS', 'SMS'),
    ('CORREO', 'Correo'),
]
ESTADO_NOTFIFICACION = [
    ('ASIGNADA', 'Asignada'),
    ('NO ASIGNADA', 'No asignada')
]
class Notificacion(models.Model):
    tipo_notificacion = models.CharField(max_length=120, choices=TIPO_NOTIFICACION, verbose_name='Tipo de Notificacion')
    canal_notificacion = models.CharField(max_length=120, choices=CANAL_NOTIFICACION, verbose_name='Canal de Notificacion')
    estado_notificacion = models.CharField(max_length=120, choices=ESTADO_NOTFIFICACION, verbose_name='Estado de Notificacion')
    fk_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    
    def __str__(self):
        return str(self.id)
      
    class Meta:
        verbose_name = 'Notificacion'
        verbose_name_plural = 'Notificaciones'
        db_table = 'notificaciones'
#--------------------------------Modulo de Gestión de Encuestas----------------------------
class Encuesta(models.Model):
    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('inactiva', 'Inactiva'),
    ]

    nombre = models.CharField(max_length=100,unique=True)
    estado = models.CharField(max_length=20,choices=ESTADO_CHOICES,default='activa')
    fk_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    form_id = models.CharField(max_length=100, blank=True, null=True)  # ID del formulario de Google Forms
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_envio = models.DateTimeField(blank=True, null=True)  # Fecha cuando se envía la encuesta
    miembros = models.ManyToManyField(Usuario, related_name='encuestas', blank=True)  # Miembros seleccionados para la encuesta
       
      
    def __str__(self):
        return str(self.nombre)
      
    class Meta:
        verbose_name = 'Encuesta'
        verbose_name_plural = 'Encuestas'
        db_table = 'encuesta'

class Pregunta(models.Model):
    TIPO_CHOICES = [
        ('short_answer', 'Respuesta corta'),
        ('paragraph', 'Párrafo'),
        ('multiple_choice', 'Opción múltiple'),
        ('check_boxes', 'Casillas de verificación'),
        ('dropdown', 'Lista desplegable'),
        ('linear_scale', 'Escala lineal'),
        ('date', 'Fecha'),
        ('time', 'Hora'),
    ]
    
    encuesta = models.ForeignKey(Encuesta, on_delete=models.CASCADE, related_name='preguntas')
    pregunta = models.CharField(max_length=500)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    opciones = models.JSONField(blank=True, null=True)  # Para opciones en multiple_choice, check_boxes, dropdown
    requerida = models.BooleanField(default=False)
    orden = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.pregunta
    
    class Meta:
        verbose_name = 'Pregunta'
        verbose_name_plural = 'Preguntas'
        db_table = 'pregunta'
        ordering = ['orden']
   
 #--------------------------------Modulo Gestión de reportes estadisticas----------------------------
class Reportes_estadisticas(models.Model):
    TIPO_REPORTE_CHOICES = [
        ('membresia', 'Membresia'),
        ('asistencia', 'Asistencia'),
        ('elemento', 'Elemento'),
    ]
    tipo_reporte = models.CharField(max_length=20,choices=TIPO_REPORTE_CHOICES,default='membresia')
    descripcion = models.TextField()
    fecha_generacion = models.DateField(default=datetime.now)
    fk_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'
        db_table = 'Reporte'

#--------------------------------Modulo Gestión de reportes y PQRS------------------------

class Soporte_PQRS(models.Model):
    TIPO_PQRS_CHOICES = [
        ('peticion', 'Peticion'),
        ('queja', 'Queja'),
        ('reclamo', 'Reclamo'),
        ('sugerencia', 'Sugerencia'),
    ]
    tipo = models.CharField(max_length=20,choices=TIPO_PQRS_CHOICES,default='peticion')
    descripcion = models.TextField()
    fecha_ingreso = models.DateField(default=datetime.now)
    ESTADO_CHOICES = [
    ('pendiente', 'pendiente'),
    ('en_proceso', 'en_proceso'),
    ('solucionada', 'solucionada'),
    ]

    estado = models.CharField(max_length=20,choices=ESTADO_CHOICES,default='pendiente')
    fk_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    
    def __str__(self):
      return str(self.id)
        
    class Meta:   
        verbose_name = 'PQRS'
        verbose_name_plural = 'PQRS'
        db_table = 'PQRS'
        

#--------------------NUTRICION------------------

class Nutricion(models.Model):

    NIVEL_ACTIVIDAD = [
        ('bajo', 'Bajo'),
        ('medio', 'Medio'),
        ('alto', 'Alto'),
    ]

    TIPO_OBJETIVO = [
        ('perder_peso', 'Perder Peso'),
        ('mantener', 'Mantener'),
        ('ganar_masa', 'Ganar Masa Muscular'),
    ]

    TIPO_DIETA = [
        ('keto', 'Keto'),
        ('balanceada', 'Balanceada'),
        ('hiperproteica', 'Hiperproteica'),
    ]

    nivel_actividad = models.CharField(max_length=20, choices=NIVEL_ACTIVIDAD)
    tipo_objetivo = models.CharField(max_length=20, choices=TIPO_OBJETIVO)
    tipo_dieta = models.CharField(max_length=40, choices=TIPO_DIETA)

    fk_Usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.fk_Usuario.nombre_usuario)
    
    class Meta:
        db_table = "Nutricion"
        verbose_name = "Nutricion"
        verbose_name_plural = "Nutriciones"
        

#------------REGISTRO DE VISITANTES----------------
    
class Registrovisitantestemporales(models.Model):
    fecha_registro = models.DateField(default=datetime.now)
    fk_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def _str_(self):
        return str(self.fk_usuario.nombre_usuario)

    class Meta:
        verbose_name = 'Registro_Visitante'
        verbose_name_plural = 'Registro_Visitantes'
        db_table = 'registro_Visitantes'

#-----------TURNO DE ENTRENADORES----------------

class Turnosentrenadores(models.Model):
    JORNADA_CHOICES = [
        ('mañana', 'Mañana'),
        ('tarde', 'Tarde'),
    ]

    administrador = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='turnos_entrenador'
    )

    fecha_turno_inicio = models.DateField(default=datetime.now)
    fecha_turno_final = models.DateField(default=datetime.now)
    jornada = models.CharField(max_length=10, choices=JORNADA_CHOICES)

    def __str__(self):
        if self.administrador:
            return f"{self.administrador.username} - {self.jornada}"
        return f"Turno {self.id}"

    class Meta:
        verbose_name = "Turno Entrenador"
        verbose_name_plural = "Turnos Entrenadores"
        db_table = "turno_entrenadores"
#-----------------IMC------------------------------

class Masa_corporal (models.Model):
    peso_cliente=models.DecimalField(max_digits=10, decimal_places=2)
    fecha_control=models.DateField()
    altura_cliente=models.DecimalField(max_digits=10, decimal_places=2)
    fk_Nutricion=models.ForeignKey(Nutricion, on_delete=models.CASCADE ,verbose_name='Nutricion')
   
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table='Masa_corporal'
        verbose_name='Masa_corporal'
        verbose_name_plural='Masas_corporales'
        
#------------RUTINA----------------

class Rutina(models.Model):
    tipo = models.CharField(max_length=50,
        choices=[
            ('FUERZA', 'Fuerza'),
            ('CARDIO', 'Cardio'),
            ('FUNCIONAL', 'Funcional'),
        ],
    )

    disponibilidad_de_dias = models.IntegerField()

    distribucion = models.CharField(
        max_length=30,
        choices=[
            ('SUPERIOR', 'Superior'),
            ('INFERIOR', 'Inferior'),
            ('COMPLETA', 'Cuerpo completo'),
        ]
    )

    fk_imc = models.ForeignKey(Masa_corporal,on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Rutina'
        verbose_name_plural = 'Rutinas'
        db_table = 'rutina'

    def __str__(self):
        return str(self.id)
    
'''----------certificaciones-----------'''

class Certificacion_interna(models.Model):
    descripcion_certificacion=models.CharField(max_length=500)
    fecha_certificacion=models.DateField(auto_now=False, auto_now_add=False)
    fk_membresia=models.ForeignKey(Membresia, on_delete=models.CASCADE, verbose_name='Membresía')
    descargado = models.BooleanField(default=False)
    def __str__(self):
        return str(self.id) 
    class Meta:
        db_table='Certificacion_interna'
        verbose_name='Certificacion_interna'
        verbose_name_plural='Certificaciones_internas'

#---------sanciones----------
class Sancion(models.Model):
    
    Tipo_sancion_chioce=[
        ('leve','Leve'),
        ('moderada','Moderada'),
        ('grave','Grave')
    ]
    Estado_choice=[
        ('activa','Activa'),
        ('inactiva','Inactiva'),
        ('pendiente','Pendiente')
    ]
    motivo_sancion=models.CharField(max_length=350)
    tipo_sancion=models.CharField(max_length=80,choices=Tipo_sancion_chioce)
    fecha_inicio=models.DateField()
    duracion_sancion=models.IntegerField()
    fecha_fin=models.DateField()
    estado=models.CharField(max_length=80,choices=Estado_choice)
    fk_usuario=models.ForeignKey(Usuario, on_delete=models.CASCADE, verbose_name='Usuario')
    
    def __str__(self):
        return self.id
    
    class Meta:
        db_table='Sancion'
        verbose_name='Sancion'
        verbose_name_plural='Sanciones'
        


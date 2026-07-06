
# Create your tests here.

from decimal import Decimal
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from .models import (
    Usuario,
    Membresia,
    Asistencia,
    Categoria,
    Elemento,
    Mantenimiento,
    Notificacion,
    Encuesta,
    Pregunta,
    Reportes_estadisticas,
    Soporte_PQRS,
    Nutricion,
    Registrovisitantestemporales,
    Turnosentrenadores,
    Masa_corporal,
    Rutina,
    Certificacion_interna,
    Sancion,
)


# ---------------------------------------------------------------------------
# Helpers para crear objetos base reutilizables en varios tests
# ---------------------------------------------------------------------------
def crear_usuario(documento="123456789", correo="juan@example.com", username="jdoe"):
    user = User.objects.create_user(
        username=username, password="clave12345", email="viejo@example.com"
    )
    return Usuario.objects.create(
        user=user,
        documento=documento,
        nombre_usuario="Juan",
        apellido_usuario="Perez",
        fecha_nacimiento=date(1995, 5, 20),
        telefono_usuario="3001234567",
        correo_usuario=correo,
        peso_usuario=Decimal("70.50"),
        altura_usuario=Decimal("1.75"),
        genero_usuario="M",
        rol="Cliente",
        tipo_documento="CC",
        estado="activo",
    )


# ---------------------------------------------------------------------------
# Usuario
# ---------------------------------------------------------------------------
class UsuarioModelTest(TestCase):
    def setUp(self):
        self.usuario = crear_usuario()

    def test_str_representation(self):
        self.assertEqual(str(self.usuario), "123456789/Juan")

    def test_fecha_registro_default_hoy(self):
        self.assertEqual(self.usuario.fecha_registro, date.today())

    def test_save_sincroniza_email_del_user(self):
        self.usuario.correo_usuario = "nuevo@example.com"
        self.usuario.save()
        self.usuario.user.refresh_from_db()
        self.assertEqual(self.usuario.user.email, "nuevo@example.com")

    def test_documento_unico(self):
        otro_user = User.objects.create_user(username="otro", password="x")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Usuario.objects.create(
                    user=otro_user,
                    documento="123456789",  # duplicado
                    nombre_usuario="Otro",
                    apellido_usuario="Usuario",
                    fecha_nacimiento=date(1990, 1, 1),
                    telefono_usuario="3000000000",
                    correo_usuario="otro@example.com",
                    peso_usuario=Decimal("60.00"),
                    altura_usuario=Decimal("1.60"),
                    estado="activo",
                )

    def test_correo_unico(self):
        otro_user = User.objects.create_user(username="otro2", password="x")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Usuario.objects.create(
                    user=otro_user,
                    documento="987654321",
                    nombre_usuario="Otro",
                    apellido_usuario="Usuario",
                    fecha_nacimiento=date(1990, 1, 1),
                    telefono_usuario="3000000000",
                    correo_usuario="juan@example.com",  # duplicado
                    peso_usuario=Decimal("60.00"),
                    altura_usuario=Decimal("1.60"),
                    estado="activo",
                )

    def test_tipo_documento_default(self):
        self.assertEqual(self.usuario.tipo_documento, "CC")


# ---------------------------------------------------------------------------
# Membresia
# ---------------------------------------------------------------------------
class MembresiaModelTest(TestCase):
    def setUp(self):
        self.usuario = crear_usuario()

    def test_creacion_genera_qr(self):
        membresia = Membresia.objects.create(estado="activo", fk_usuario=self.usuario)
        self.assertTrue(membresia.qr_code)
        self.assertIn("qr_", membresia.qr_code.name)

    def test_str_representation(self):
        membresia = Membresia.objects.create(estado="activo", fk_usuario=self.usuario)
        self.assertEqual(
            str(membresia), f"Juan Perez - {membresia.id}"
        )

    def test_es_valida_sin_fecha_fin(self):
        membresia = Membresia.objects.create(estado="activo", fk_usuario=self.usuario)
        self.assertTrue(membresia.es_valida)

        membresia.estado = "inactivo"
        membresia.save()
        self.assertFalse(membresia.es_valida)

    def test_es_valida_con_fecha_fin_vencida(self):
        membresia = Membresia.objects.create(
            estado="activo",
            fecha_fin=timezone.now().date() - timedelta(days=1),
            fk_usuario=self.usuario,
        )
        self.assertFalse(membresia.es_valida)

    def test_es_valida_con_fecha_fin_vigente(self):
        membresia = Membresia.objects.create(
            estado="activo",
            fecha_fin=timezone.now().date() + timedelta(days=10),
            fk_usuario=self.usuario,
        )
        self.assertTrue(membresia.es_valida)

    def test_dias_para_vencer_sin_fecha_fin(self):
        membresia = Membresia.objects.create(estado="activo", fk_usuario=self.usuario)
        self.assertIsNone(membresia.dias_para_vencer)

    def test_dias_para_vencer_con_fecha_futura(self):
        membresia = Membresia.objects.create(
            estado="activo",
            fecha_fin=timezone.now().date() + timedelta(days=5),
            fk_usuario=self.usuario,
        )
        self.assertEqual(membresia.dias_para_vencer, 5)

    def test_dias_para_vencer_no_negativo(self):
        membresia = Membresia.objects.create(
            estado="activo",
            fecha_fin=timezone.now().date() - timedelta(days=5),
            fk_usuario=self.usuario,
        )
        self.assertEqual(membresia.dias_para_vencer, 0)


# ---------------------------------------------------------------------------
# Asistencia
# ---------------------------------------------------------------------------
class AsistenciaModelTest(TestCase):
    def setUp(self):
        self.usuario = crear_usuario()
        self.membresia = Membresia.objects.create(
            estado="activo", fk_usuario=self.usuario
        )

    def test_creacion_y_fecha_default(self):
        asistencia = Asistencia.objects.create(fk_membresia=self.membresia)
        self.assertEqual(asistencia.fecha_asistencia, date.today())

    def test_str_representation(self):
        asistencia = Asistencia.objects.create(fk_membresia=self.membresia)
        esperado = f"{asistencia.id}-{asistencia.fecha_asistencia}/Juan"
        self.assertEqual(str(asistencia), esperado)


# ---------------------------------------------------------------------------
# Categoria y Elemento
# ---------------------------------------------------------------------------
class CategoriaModelTest(TestCase):
    def test_str_y_unicidad(self):
        categoria = Categoria.objects.create(
            nombre_categoria="Cardio", descripcion="Máquinas de cardio"
        )
        self.assertEqual(str(categoria), "Cardio")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Categoria.objects.create(
                    nombre_categoria="Cardio", descripcion="Duplicado"
                )


class ElementoModelTest(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(
            nombre_categoria="Fuerza", descripcion="Máquinas de fuerza"
        )

    def test_creacion_y_defaults(self):
        elemento = Elemento.objects.create(
            serial="EL-001",
            marca="TechnoGym",
            nombre_elemento="Press de banca",
            peso_elemento=Decimal("80.00"),
            estado="activo",
            fecha_ingreso=date.today(),
            nombre_categoria=self.categoria,
        )
        self.assertEqual(elemento.unidad_peso, "kg")
        self.assertEqual(elemento.cantidad, 1)
        self.assertEqual(str(elemento), "Press de banca")

    def test_serial_unico(self):
        Elemento.objects.create(
            serial="EL-002",
            marca="Marca",
            nombre_elemento="Elemento 1",
            peso_elemento=Decimal("10.00"),
            estado="activo",
            fecha_ingreso=date.today(),
            nombre_categoria=self.categoria,
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Elemento.objects.create(
                    serial="EL-002",
                    marca="Otra",
                    nombre_elemento="Elemento 2",
                    peso_elemento=Decimal("20.00"),
                    estado="activo",
                    fecha_ingreso=date.today(),
                    nombre_categoria=self.categoria,
                )


class MantenimientoModelTest(TestCase):
    def setUp(self):
        categoria = Categoria.objects.create(
            nombre_categoria="Fuerza", descripcion="Máquinas de fuerza"
        )
        self.elemento = Elemento.objects.create(
            serial="EL-010",
            marca="Marca",
            nombre_elemento="Elemento",
            peso_elemento=Decimal("10.00"),
            estado="activo",
            fecha_ingreso=date.today(),
            nombre_categoria=categoria,
        )

    def test_creacion(self):
        mantenimiento = Mantenimiento.objects.create(
            fecha_programada=date.today(),
            tipo_mantenimiento="preventivo",
            estado="pendiente",
            nombre_elemento=self.elemento,
            descripcion="Revisión de rutina",
        )
        self.assertEqual(str(mantenimiento), str(mantenimiento.id))
        self.assertEqual(mantenimiento.estado, "pendiente")


# ---------------------------------------------------------------------------
# Notificacion
# ---------------------------------------------------------------------------
class NotificacionModelTest(TestCase):
    def setUp(self):
        self.usuario = crear_usuario()

    def test_creacion_y_str(self):
        notificacion = Notificacion.objects.create(
            tipo_notificacion="MEMBRESIA",
            canal_notificacion="CORREO",
            estado_notificacion="ASIGNADA",
            detalle_notificacion="Bienvenida",
            fk_usuario=self.usuario,
        )
        self.assertIsNotNone(notificacion.fecha_creacion)
        esperado = (
            f"Membresía - Juan "
            f"({notificacion.fecha_creacion.strftime('%d/%m/%Y')})"
        )
        self.assertEqual(str(notificacion), esperado)

    def test_ordering_por_fecha_creacion_desc(self):
        n1 = Notificacion.objects.create(
            tipo_notificacion="MEMBRESIA",
            canal_notificacion="CORREO",
            estado_notificacion="ASIGNADA",
            detalle_notificacion="Bienvenida",
            fk_usuario=self.usuario,
        )
        n2 = Notificacion.objects.create(
            tipo_notificacion="ASISTENCIA",
            canal_notificacion="SMS",
            estado_notificacion="NO ASIGNADA",
            detalle_notificacion="Inasistencia",
            fk_usuario=self.usuario,
        )
        notificaciones = list(Notificacion.objects.all())
        self.assertEqual(notificaciones[0], n2)
        self.assertEqual(notificaciones[1], n1)


# ---------------------------------------------------------------------------
# Encuesta y Pregunta
# ---------------------------------------------------------------------------
class EncuestaModelTest(TestCase):
    def setUp(self):
        self.usuario = crear_usuario()
        self.miembro = crear_usuario(
            documento="999999999", correo="miembro@example.com", username="miembro"
        )

    def test_creacion_y_str(self):
        encuesta = Encuesta.objects.create(
            nombre="Satisfacción 2026", fk_usuario=self.usuario
        )
        encuesta.miembros.add(self.miembro)

        self.assertEqual(str(encuesta), "Satisfacción 2026")
        self.assertEqual(encuesta.estado, "activa")
        self.assertIn(self.miembro, encuesta.miembros.all())

    def test_nombre_unico(self):
        Encuesta.objects.create(nombre="Encuesta X", fk_usuario=self.usuario)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Encuesta.objects.create(
                    nombre="Encuesta X", fk_usuario=self.usuario
                )


class PreguntaModelTest(TestCase):
    def setUp(self):
        self.usuario = crear_usuario()
        self.encuesta = Encuesta.objects.create(
            nombre="Encuesta Preguntas", fk_usuario=self.usuario
        )

    def test_creacion_y_str(self):
        pregunta = Pregunta.objects.create(
            encuesta=self.encuesta,
            pregunta="¿Qué tan satisfecho estás?",
            tipo="linear_scale",
            requerida=True,
            orden=1,
        )
        self.assertEqual(str(pregunta), "¿Qué tan satisfecho estás?")
        self.assertFalse(pregunta.opciones)

    def test_ordering_por_orden(self):
        p2 = Pregunta.objects.create(
            encuesta=self.encuesta, pregunta="Segunda", tipo="short_answer", orden=2
        )
        p1 = Pregunta.objects.create(
            encuesta=self.encuesta, pregunta="Primera", tipo="short_answer", orden=1
        )
        preguntas = list(self.encuesta.preguntas.all())
        self.assertEqual(preguntas[0], p1)
        self.assertEqual(preguntas[1], p2)


# ---------------------------------------------------------------------------
# Reportes_estadisticas
# ---------------------------------------------------------------------------
class ReportesEstadisticasModelTest(TestCase):
    def setUp(self):
        self.usuario = crear_usuario()

    def test_creacion_y_str(self):
        reporte = Reportes_estadisticas.objects.create(
            tipo_reporte="usuarios",
            tipo_archivo="PDF",
            descripcion="Reporte mensual de usuarios",
            fk_usuario=self.usuario,
        )
        self.assertEqual(str(reporte), "Usuarios - PDF")
        self.assertIsNotNone(reporte.fecha_generacion)


# ---------------------------------------------------------------------------
# Soporte_PQRS
# ---------------------------------------------------------------------------
class SoportePQRSModelTest(TestCase):
    def setUp(self):
        self.usuario = crear_usuario()

    def test_creacion_y_defaults(self):
        pqrs = Soporte_PQRS.objects.create(
            descripcion="No funciona la máquina de cardio",
            fk_usuario=self.usuario,
        )
        self.assertEqual(pqrs.tipo, "peticion")
        self.assertEqual(pqrs.estado, "pendiente")
        self.assertEqual(pqrs.fecha_ingreso, date.today())
        self.assertEqual(str(pqrs), str(pqrs.id))


# ---------------------------------------------------------------------------
# Nutricion y Masa_corporal
# ---------------------------------------------------------------------------
class NutricionModelTest(TestCase):
    def setUp(self):
        self.usuario = crear_usuario()

    def test_creacion_y_str(self):
        nutricion = Nutricion.objects.create(
            nivel_actividad_fisica="medio",
            objetivo_nutricional="perder_peso",
            tipo_plan_alimenticio="balanceada",
            fk_Usuario=self.usuario,
        )
        self.assertEqual(str(nutricion), "Juan")


class MasaCorporalModelTest(TestCase):
    def setUp(self):
        self.usuario = crear_usuario()
        self.nutricion = Nutricion.objects.create(
            nivel_actividad_fisica="alto",
            objetivo_nutricional="ganar_masa",
            tipo_plan_alimenticio="hiperproteica",
            fk_Usuario=self.usuario,
        )

    def test_creacion_y_str(self):
        masa = Masa_corporal.objects.create(
            peso_cliente=Decimal("75.00"),
            fecha_control=date.today(),
            altura_cliente=Decimal("1.75"),
            fk_Nutricion=self.nutricion,
            imc=24.5,
            estado_imc="Normal",
        )
        self.assertEqual(str(masa), "Juan - 123456789")
        self.assertIn(masa, self.nutricion.nutricion.all())


# ---------------------------------------------------------------------------
# Registrovisitantestemporales
# ---------------------------------------------------------------------------
class RegistroVisitantesModelTest(TestCase):
    def test_creacion_y_str(self):
        visitante = Registrovisitantestemporales.objects.create(
            nombre="Carlos Gómez", cedula="1122334455"
        )
        self.assertEqual(visitante.fecha_registro, date.today())
        self.assertEqual(str(visitante), "Carlos Gómez - 1122334455")


# ---------------------------------------------------------------------------
# Turnosentrenadores
# ---------------------------------------------------------------------------
class TurnosEntrenadoresModelTest(TestCase):
    def test_str_sin_administrador(self):
        turno = Turnosentrenadores.objects.create(jornada="mañana")
        self.assertEqual(str(turno), f"Turno {turno.id}")

    def test_creacion_con_administrador(self):
        # NOTA: el método __str__ del modelo referencia
        # `self.administrador.username`, pero `administrador` es una
        # instancia de Usuario (no de User) y Usuario no define el campo
        # `username`. Esto provoca un AttributeError al llamar str() sobre
        # un turno con administrador asignado. Se documenta aquí el
        # comportamiento actual; si se corrige el modelo (por ejemplo usando
        # `self.administrador.nombre_usuario` o
        # `self.administrador.user.username`), este test deberá actualizarse.
        usuario = crear_usuario()
        turno = Turnosentrenadores.objects.create(
            administrador=usuario, jornada="tarde"
        )
        with self.assertRaises(AttributeError):
            str(turno)


# ---------------------------------------------------------------------------
# Rutina
# ---------------------------------------------------------------------------
class RutinaModelTest(TestCase):
    def setUp(self):
        usuario = crear_usuario()
        nutricion = Nutricion.objects.create(
            nivel_actividad_fisica="medio",
            objetivo_nutricional="mantener",
            tipo_plan_alimenticio="balanceada",
            fk_Usuario=usuario,
        )
        self.masa = Masa_corporal.objects.create(
            peso_cliente=Decimal("70.00"),
            fecha_control=date.today(),
            altura_cliente=Decimal("1.70"),
            fk_Nutricion=nutricion,
        )

    def test_creacion_y_str(self):
        rutina = Rutina.objects.create(
            tipo_rutina="FUERZA",
            dias_disponibles=4,
            distribucion_rutina="SUPERIOR",
            fk_imc=self.masa,
        )
        self.assertEqual(str(rutina), str(rutina.id))
        self.assertEqual(rutina.dias_disponibles, 4)


# ---------------------------------------------------------------------------
# Certificacion_interna
# ---------------------------------------------------------------------------
class CertificacionInternaModelTest(TestCase):
    def setUp(self):
        usuario = crear_usuario()
        self.membresia = Membresia.objects.create(estado="activo", fk_usuario=usuario)

    def test_creacion_y_default_descargado(self):
        certificacion = Certificacion_interna.objects.create(
            descripcion_certificacion="Curso de primeros auxilios",
            fecha_certificacion=date.today(),
            fk_membresia=self.membresia,
        )
        self.assertFalse(certificacion.descargado)
        self.assertEqual(str(certificacion), str(certificacion.id))


# ---------------------------------------------------------------------------
# Sancion
# ---------------------------------------------------------------------------
class SancionModelTest(TestCase):
    def setUp(self):
        self.usuario = crear_usuario()

    def test_creacion(self):
        sancion = Sancion.objects.create(
            motivo_sancion="Uso inadecuado de equipo",
            tipo_sancion="leve",
            fecha_inicio=date.today(),
            duracion_sancion=7,
            fecha_fin=date.today() + timedelta(days=7),
            estado="activa",
            fk_usuario=self.usuario,
        )
        self.assertEqual(sancion.tipo_sancion, "leve")
        self.assertEqual(sancion.duracion_sancion, 7)

    def test_str_tiene_bug_de_atributo(self):
        # NOTA: el método __str__ de Sancion referencia `self.fk_Usuario`
        # (con "U" mayúscula), pero el campo del modelo se llama
        # `fk_usuario` (minúscula). Esto provoca un AttributeError al
        # invocar str() sobre cualquier instancia de Sancion. Se documenta
        # el comportamiento actual; si se corrige el nombre del atributo en
        # el modelo, este test deberá actualizarse para verificar la salida
        # esperada, por ejemplo "Juan - 123456789".
        sancion = Sancion.objects.create(
            motivo_sancion="Falta de respeto",
            tipo_sancion="moderada",
            fecha_inicio=date.today(),
            duracion_sancion=15,
            fecha_fin=date.today() + timedelta(days=15),
            estado="pendiente",
            fk_usuario=self.usuario,
        )
        with self.assertRaises(AttributeError):
            str(sancion)
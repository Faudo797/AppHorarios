from datetime import time

from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Asignatura, Aula, Clase, Estudiante, Grado, Hora, Profesor


User = get_user_model()


class BaseScheduleTestCase(TestCase):
    def setUp(self):
        self.asignatura = Asignatura.objects.create(
            codigo_asignatura='MAT',
            nombre='Matematicas',
        )
        self.grado_a = Grado.objects.create(codigo_grado='6A', nombre='Sexto A')
        self.grado_b = Grado.objects.create(codigo_grado='6B', nombre='Sexto B')
        self.aula = Aula.objects.create(nombre='Aula 101', capacidad=35)
        self.hora = Hora.objects.create(hora_inicio=time(7, 0), hora_fin=time(8, 0))

        self.profesor_user = User.objects.create_user(
            username='PROF001',
            password='123456',
            rol='profesor',
        )
        self.profesor = Profesor.objects.create(
            codigo_profesor='PROF001',
            identificacion='9001',
            primer_nombre='Ana',
            primer_apellido='Lopez',
            asignatura=self.asignatura,
            usuario=self.profesor_user,
        )
        self.profesor.grados.add(self.grado_a)


class HoraModelTests(TestCase):
    def test_hora_fin_debe_ser_posterior_a_hora_inicio(self):
        hora = Hora(hora_inicio=time(9, 0), hora_fin=time(8, 0))

        with self.assertRaises(ValidationError):
            hora.full_clean()


class ClaseModelTests(BaseScheduleTestCase):
    def test_no_permite_conflicto_de_grado_en_mismo_bloque(self):
        Clase.objects.create(
            descripcion_clase='Algebra',
            profesor=self.profesor,
            aula=self.aula,
            hora=self.hora,
            dia='LU',
            grado=self.grado_a,
        )

        conflicto = Clase(
            descripcion_clase='Geometria',
            profesor=self.profesor,
            aula=self.aula,
            hora=self.hora,
            dia='LU',
            grado=self.grado_a,
        )

        with self.assertRaises(ValidationError):
            conflicto.full_clean()

    def test_no_permite_programar_profesor_en_grado_no_asignado(self):
        clase = Clase(
            descripcion_clase='Matematicas',
            profesor=self.profesor,
            aula=self.aula,
            hora=self.hora,
            dia='MA',
            grado=self.grado_b,
        )

        with self.assertRaises(ValidationError):
            clase.full_clean()


class HorarioViewTests(BaseScheduleTestCase):
    def setUp(self):
        super().setUp()
        self.estudiante_user = User.objects.create_user(
            username='EST001',
            password='123456',
            rol='estudiante',
        )
        self.estudiante = Estudiante.objects.create(
            codigo_estudiante='EST001',
            identificacion='8001',
            primer_nombre='Luis',
            primer_apellido='Perez',
            grado=self.grado_a,
            usuario=self.estudiante_user,
        )
        self.clase = Clase.objects.create(
            descripcion_clase='Algebra',
            profesor=self.profesor,
            aula=self.aula,
            hora=self.hora,
            dia='LU',
            grado=self.grado_a,
        )

    def test_estudiante_visualiza_su_horario(self):
        self.client.login(username='EST001', password='123456')

        response = self.client.get(reverse('horario_view'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Matematicas')
        self.assertContains(response, 'Aula 101')
        self.assertContains(response, 'Luis Perez')

    def test_admin_redirige_a_busqueda_si_no_indica_usuario(self):
        admin_user = User.objects.create_user(
            username='ADMIN001',
            password='123456',
            rol='admin',
        )
        self.client.login(username='ADMIN001', password='123456')

        response = self.client.get(reverse('horario_view'))

        self.assertRedirects(response, reverse('ver_horarios'))

"""
=============================================================================
PRUEBAS DE CALIDAD Y RENDIMIENTO — ISO 25010
AppHorarios — Sistema de Gestión de Horarios Escolares
=============================================================================
Dimensiones evaluadas:
  1. Adecuación Funcional  — Pruebas CRUD, generador, validaciones
  2. Eficiencia de Desempeño — Tiempos de respuesta, stress del generador
  3. Seguridad — Auth, CSRF, roles, inyección
  4. Fiabilidad — Manejo de errores, integridad referencial
  5. Mantenibilidad — Código muerto, debug prints, complejidad
=============================================================================
"""
import time
import json
import datetime

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model

from apphorarios.models import (
    Asignatura, Aula, Profesor, Estudiante, Grado, Hora,
    Ficha, FichaAsignada, ConfiguracionColegio,
)
from apphorarios.generador import generar_horario

User = get_user_model()


# =====================================================================
#  FIXTURES BASE — Reutilizable por todas las pruebas
# =====================================================================
class BaseTestCase(TestCase):
    """Configura un escenario mínimo con admin, profesor, estudiante."""

    def setUp(self):
        # Admin
        self.admin_user = User.objects.create_user(
            username='admin_test', password='Admin123!', rol='admin'
        )
        # Profesor
        self.prof_user = User.objects.create_user(
            username='prof_test', password='Prof123!', rol='profesor'
        )
        self.asignatura = Asignatura.objects.create(
            codigo_asignatura='MAT', nombre='Matemáticas',
            abreviatura='MAT', color='#3b82f6'
        )
        self.grado = Grado.objects.create(
            codigo_grado='5TO', nombre='Quinto'
        )
        self.aula = Aula.objects.create(
            nombre='Aula 101', abreviatura='A101', capacidad=35
        )
        self.hora1 = Hora.objects.create(
            hora_inicio=datetime.time(7, 0), hora_fin=datetime.time(8, 0)
        )
        self.hora2 = Hora.objects.create(
            hora_inicio=datetime.time(8, 0), hora_fin=datetime.time(9, 0)
        )
        self.profesor = Profesor.objects.create(
            codigo_profesor='P-TEST', identificacion='99001',
            primer_nombre='Carlos', primer_apellido='Pérez',
            abreviatura='CarP', usuario=self.prof_user
        )
        self.profesor.asignaturas.add(self.asignatura)

        # Estudiante
        self.est_user = User.objects.create_user(
            username='est_test', password='Est123!', rol='estudiante'
        )
        self.estudiante = Estudiante.objects.create(
            codigo_estudiante='E-TEST', identificacion='88001',
            primer_nombre='Luis', primer_apellido='Gómez',
            grado=self.grado, usuario=self.est_user
        )

        # Ficha
        self.ficha = Ficha.objects.create(
            profesor=self.profesor, asignatura=self.asignatura,
            grado=self.grado, horas_totales=4
        )

        # Cliente
        self.client = Client()


# =====================================================================
#  1. ADECUACIÓN FUNCIONAL
# =====================================================================
class TestFuncionalModelos(BaseTestCase):
    """Pruebas de validación de modelos."""

    def test_crear_asignatura_completa(self):
        """Verificar que una asignatura se crea correctamente."""
        a = Asignatura.objects.create(
            codigo_asignatura='FIS', nombre='Física',
            abreviatura='FIS', color='#2563eb'
        )
        self.assertEqual(a.nombre, 'Física')
        self.assertEqual(a.color, '#2563eb')

    def test_crear_aula_con_capacidad_valida(self):
        """Verificar creación de aula con datos correctos."""
        aula = Aula.objects.create(
            nombre='Lab Ciencias', abreviatura='LAB', capacidad=30
        )
        self.assertEqual(aula.capacidad, 30)

    def test_ficha_asignada_unique_constraint(self):
        """No se puede asignar dos fichas al mismo aula+hora+dia."""
        FichaAsignada.objects.create(
            ficha=self.ficha, dia='LU', hora=self.hora1, aula=self.aula
        )
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            FichaAsignada.objects.create(
                ficha=self.ficha, dia='LU', hora=self.hora1, aula=self.aula
            )

    def test_configuracion_colegio_singleton(self):
        """ConfiguracionColegio funciona como singleton."""
        c1 = ConfiguracionColegio.get_config()
        c2 = ConfiguracionColegio.get_config()
        self.assertEqual(c1.id, c2.id)

    def test_profesor_str(self):
        """String representation del profesor."""
        self.assertIn('Carlos', str(self.profesor))

    def test_ficha_str(self):
        """String representation de la ficha."""
        s = str(self.ficha)
        self.assertTrue(len(s) > 0)


class TestFuncionalAPIs(BaseTestCase):
    """Pruebas CRUD via APIs JSON."""

    def _admin_login(self):
        self.client.login(username='admin_test', password='Admin123!')

    def test_api_crear_asignatura(self):
        self._admin_login()
        res = self.client.post(
            reverse('api_guardar_asignatura'),
            json.dumps({
                'codigo_asignatura': 'ESP', 'nombre': 'Español',
                'abreviatura': 'ESP', 'color': '#ef4444'
            }),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get('success'))
        self.assertTrue(Asignatura.objects.filter(nombre='Español').exists())

    def test_api_editar_asignatura(self):
        self._admin_login()
        res = self.client.post(
            reverse('api_guardar_asignatura'),
            json.dumps({
                'id': self.asignatura.id,
                'codigo_asignatura': 'MAT', 'nombre': 'Matemáticas Avanzadas',
                'abreviatura': 'MATA', 'color': '#1e40af'
            }),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        self.asignatura.refresh_from_db()
        self.assertEqual(self.asignatura.nombre, 'Matemáticas Avanzadas')

    def test_api_eliminar_asignatura(self):
        self._admin_login()
        a = Asignatura.objects.create(
            codigo_asignatura='TMP', nombre='Temporal',
            abreviatura='TMP', color='#000000'
        )
        res = self.client.delete(
            reverse('api_eliminar_asignatura', args=[a.id])
        )
        self.assertEqual(res.status_code, 200)
        self.assertFalse(Asignatura.objects.filter(id=a.id).exists())

    def test_api_crear_aula(self):
        self._admin_login()
        res = self.client.post(
            reverse('api_guardar_aula'),
            json.dumps({
                'nombre': 'Cancha', 'abreviatura': 'CAN', 'capacidad': 50
            }),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(Aula.objects.filter(nombre='Cancha').exists())

    def test_api_eliminar_aula(self):
        self._admin_login()
        aula = Aula.objects.create(
            nombre='Temp Aula', abreviatura='TMP', capacidad=20
        )
        res = self.client.delete(
            reverse('api_eliminar_aula', args=[aula.id])
        )
        self.assertEqual(res.status_code, 200)
        self.assertFalse(Aula.objects.filter(id=aula.id).exists())

    def test_api_crear_ficha(self):
        self._admin_login()
        res = self.client.post(
            reverse('api_guardar_ficha'),
            json.dumps({
                'profesor_id': self.profesor.id,
                'asignatura_id': self.asignatura.id,
                'grado_id': self.grado.id,
                'horas_totales': 3
            }),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json().get('success'))

    def test_api_asignar_ficha(self):
        self._admin_login()
        res = self.client.post(
            reverse('api_asignar_ficha'),
            json.dumps({
                'ficha_id': self.ficha.id,
                'dia': 'LU',
                'hora_id': self.hora1.id,
                'aula_id': self.aula.id
            }),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json().get('success'))

    def test_api_asignar_ficha_aula_ocupada(self):
        """No se puede asignar dos fichas al mismo aula+hora+dia."""
        self._admin_login()
        FichaAsignada.objects.create(
            ficha=self.ficha, dia='LU', hora=self.hora1, aula=self.aula
        )
        a2 = Asignatura.objects.create(
            codigo_asignatura='FIS', nombre='Física',
            abreviatura='FIS', color='#2563eb'
        )
        g2 = Grado.objects.create(codigo_grado='6TO', nombre='Sexto')
        p2 = Profesor.objects.create(
            codigo_profesor='P-T2', identificacion='99002',
            primer_nombre='Ana', primer_apellido='R', abreviatura='AnaR'
        )
        f2 = Ficha.objects.create(
            profesor=p2, asignatura=a2, grado=g2, horas_totales=2
        )
        res = self.client.post(
            reverse('api_asignar_ficha'),
            json.dumps({
                'ficha_id': f2.id, 'dia': 'LU',
                'hora_id': self.hora1.id, 'aula_id': self.aula.id
            }),
            content_type='application/json'
        )
        data = res.json()
        self.assertFalse(data.get('success'))

    def test_api_tablero_data_completo(self):
        """El tablero retorna todas las claves esperadas."""
        self._admin_login()
        res = self.client.get(reverse('api_get_tablero_data'))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        for key in ['grados', 'horas', 'aulas', 'profesores', 'asignaturas', 'fichas', 'asignadas', 'dias']:
            self.assertIn(key, data, f"Falta clave '{key}' en respuesta del tablero")

    def test_api_tablero_data_aulas_incluye_capacidad_y_abreviatura(self):
        """Las aulas en el tablero incluyen capacidad y abreviatura."""
        self._admin_login()
        res = self.client.get(reverse('api_get_tablero_data'))
        data = res.json()
        if data['aulas']:
            aula = data['aulas'][0]
            self.assertIn('capacidad', aula)
            self.assertIn('abreviatura', aula)

    def test_api_limpiar_horario(self):
        self._admin_login()
        FichaAsignada.objects.create(
            ficha=self.ficha, dia='LU', hora=self.hora1, aula=self.aula
        )
        res = self.client.post(reverse('api_limpiar_horario'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(FichaAsignada.objects.count(), 0)


class TestFuncionalGenerador(BaseTestCase):
    """Pruebas del algoritmo de generación de horarios."""

    def _crear_escenario_completo(self):
        """Crea un escenario con 3 grados, 5 asignaturas, 4 profesores."""
        horas_extra = []
        for h, m1, m2 in [(9, 30, 30), (10, 30, 30), (11, 30, 30), (13, 0, 0)]:
            horas_extra.append(Hora.objects.create(
                hora_inicio=datetime.time(h, m1),
                hora_fin=datetime.time(h + 1, m2)
            ))

        asigs = {}
        for nombre, cod, color in [
            ('Física', 'FIS', '#2563eb'),
            ('Español', 'ESP', '#ef4444'),
            ('Inglés', 'ING', '#8b5cf6'),
            ('Sociales', 'SOC', '#f59e0b'),
        ]:
            asigs[nombre] = Asignatura.objects.create(
                codigo_asignatura=cod, nombre=nombre,
                abreviatura=cod, color=color
            )

        grados = {}
        for g_name, g_code in [('Sexto', '6TO'), ('Séptimo', '7MO')]:
            grados[g_name] = Grado.objects.create(
                codigo_grado=g_code, nombre=g_name
            )

        profs = {}
        for pn, code, ident, abbr in [
            ('Laura', 'P-LAU', '10002', 'LauG'),
            ('María', 'P-MAR', '10003', 'MarL'),
            ('Luis', 'P-LUI', '10006', 'LuiM'),
        ]:
            profs[pn] = Profesor.objects.create(
                codigo_profesor=code, identificacion=ident,
                primer_nombre=pn, primer_apellido='Test', abreviatura=abbr
            )

        # Fichas para Quinto (usa self.grado)
        Ficha.objects.create(profesor=self.profesor, asignatura=self.asignatura,
                            grado=self.grado, horas_totales=5)
        Ficha.objects.create(profesor=profs['María'], asignatura=asigs['Español'],
                            grado=self.grado, horas_totales=5)
        Ficha.objects.create(profesor=profs['Luis'], asignatura=asigs['Sociales'],
                            grado=self.grado, horas_totales=4)
        Ficha.objects.create(profesor=profs['Laura'], asignatura=asigs['Física'],
                            grado=self.grado, horas_totales=4)

        # Fichas para Sexto
        Ficha.objects.create(profesor=self.profesor, asignatura=self.asignatura,
                            grado=grados['Sexto'], horas_totales=5)
        Ficha.objects.create(profesor=profs['María'], asignatura=asigs['Español'],
                            grado=grados['Sexto'], horas_totales=5)

        return grados, asigs, profs

    def test_generador_estrategia_1111_no_repite_materia_mismo_dia(self):
        """Estrategia 1-1-1-1 no debe repetir la misma asignatura el mismo día."""
        self._crear_escenario_completo()
        FichaAsignada.objects.all().delete()
        success, msg = generar_horario(estrategia='1-1-1-1')
        self.assertTrue(success)

        # Verificar que no hay asignatura repetida en mismo día+grado
        asignaciones = FichaAsignada.objects.select_related(
            'ficha__asignatura', 'ficha__grado'
        ).all()
        seen = {}
        for a in asignaciones:
            key = (a.ficha.grado_id, a.dia, a.ficha.asignatura_id)
            seen[key] = seen.get(key, 0) + 1

        for key, count in seen.items():
            self.assertEqual(count, 1,
                f"Asignatura repetida en mismo día: grado={key[0]}, dia={key[1]}, asig={key[2]}, veces={count}")

    def test_generador_estrategia_21_bloques_consecutivos(self):
        """Estrategia 2-1-1: los bloques dobles deben ser consecutivos."""
        self._crear_escenario_completo()
        FichaAsignada.objects.all().delete()
        success, msg = generar_horario(estrategia='2-1-1')
        self.assertTrue(success)

        horas_objs = list(Hora.objects.all().order_by('hora_inicio'))
        horas_ids = [h.id for h in horas_objs]

        asignaciones = FichaAsignada.objects.select_related(
            'ficha__asignatura', 'ficha__grado'
        ).all()

        by_key = {}
        for a in asignaciones:
            key = (a.ficha.grado_id, a.dia, a.ficha.asignatura_id)
            if key not in by_key:
                by_key[key] = []
            by_key[key].append(horas_ids.index(a.hora_id))

        for key, idxs in by_key.items():
            if len(idxs) > 1:
                s = sorted(idxs)
                for i in range(len(s) - 1):
                    self.assertEqual(s[i + 1] - s[i], 1,
                        f"Bloque no consecutivo: {key}, slots: {s}")

    def test_generador_no_conflicto_profesor(self):
        """Un profesor no puede estar en dos sitios a la vez."""
        self._crear_escenario_completo()
        FichaAsignada.objects.all().delete()
        generar_horario(estrategia='2-2')

        asignaciones = FichaAsignada.objects.select_related('ficha').all()
        slots = {}
        for a in asignaciones:
            key = (a.dia, a.hora_id, a.ficha.profesor_id)
            self.assertNotIn(key, slots,
                f"Conflicto de profesor: profesor={a.ficha.profesor_id}, dia={a.dia}, hora={a.hora_id}")
            slots[key] = True

    def test_generador_no_conflicto_grado(self):
        """Un grado no puede tener dos clases simultáneas."""
        self._crear_escenario_completo()
        FichaAsignada.objects.all().delete()
        generar_horario(estrategia='2-2')

        asignaciones = FichaAsignada.objects.select_related('ficha').all()
        slots = {}
        for a in asignaciones:
            key = (a.dia, a.hora_id, a.ficha.grado_id)
            self.assertNotIn(key, slots,
                f"Conflicto de grado: grado={a.ficha.grado_id}, dia={a.dia}, hora={a.hora_id}")
            slots[key] = True


# =====================================================================
#  2. EFICIENCIA DE DESEMPEÑO
# =====================================================================
class TestRendimiento(BaseTestCase):
    """Pruebas de tiempo de respuesta y rendimiento."""

    def test_rendimiento_tablero_data(self):
        """api_get_tablero_data debe responder en menos de 500ms."""
        self.client.login(username='admin_test', password='Admin123!')
        start = time.time()
        for _ in range(10):
            self.client.get(reverse('api_get_tablero_data'))
        elapsed = (time.time() - start) / 10
        self.assertLess(elapsed, 0.5,
            f"api_get_tablero_data demasiado lento: {elapsed:.3f}s promedio")

    def test_rendimiento_login_page(self):
        """La página de login debe cargar en menos de 300ms."""
        start = time.time()
        for _ in range(10):
            self.client.get(reverse('login'))
        elapsed = (time.time() - start) / 10
        self.assertLess(elapsed, 0.3,
            f"Login page demasiado lenta: {elapsed:.3f}s promedio")

    def test_rendimiento_generador_stress(self):
        """El generador debe completar en menos de 5 segundos con escenario completo."""
        # Crear un escenario realista
        horas = [self.hora1, self.hora2]
        for h, m in [(9, 30), (10, 30), (11, 30), (13, 0)]:
            horas.append(Hora.objects.create(
                hora_inicio=datetime.time(h, m),
                hora_fin=datetime.time(h + 1, m)
            ))

        asigs = []
        for i, (nombre, cod) in enumerate([
            ('Física', 'FIS'), ('Español', 'ESP'), ('Inglés', 'ING'),
            ('Sociales', 'SOC'), ('Ed.Física', 'EFI')
        ]):
            asigs.append(Asignatura.objects.create(
                codigo_asignatura=cod, nombre=nombre,
                abreviatura=cod, color=f'#{i}00000'
            ))

        grados = [self.grado]
        for i in range(4):
            grados.append(Grado.objects.create(
                codigo_grado=f'G{i}', nombre=f'Grado{i}'
            ))

        profs = [self.profesor]
        for i in range(4):
            profs.append(Profesor.objects.create(
                codigo_profesor=f'P-S{i}', identificacion=f'20{i:03d}',
                primer_nombre=f'Prof{i}', primer_apellido='Test',
                abreviatura=f'P{i}'
            ))

        # Crear fichas
        for g in grados:
            for j, a in enumerate(asigs):
                Ficha.objects.create(
                    profesor=profs[j % len(profs)],
                    asignatura=a, grado=g, horas_totales=4
                )

        FichaAsignada.objects.all().delete()
        start = time.time()
        success, msg = generar_horario(estrategia='2-1-1')
        elapsed = time.time() - start
        self.assertTrue(success)
        self.assertLess(elapsed, 5.0,
            f"Generador demasiado lento: {elapsed:.3f}s")

    def test_rendimiento_api_asignatura_crud(self):
        """CRUD de asignaturas debe ser rápido (<200ms por operación)."""
        self.client.login(username='admin_test', password='Admin123!')

        start = time.time()
        res = self.client.post(
            reverse('api_guardar_asignatura'),
            json.dumps({
                'codigo_asignatura': 'PERF', 'nombre': 'PerfTest',
                'abreviatura': 'PER', 'color': '#000000'
            }),
            content_type='application/json'
        )
        elapsed = time.time() - start
        self.assertLess(elapsed, 0.2)
        asig_id = res.json()['id']

        start = time.time()
        self.client.delete(reverse('api_eliminar_asignatura', args=[asig_id]))
        elapsed = time.time() - start
        self.assertLess(elapsed, 0.2)


# =====================================================================
#  3. SEGURIDAD
# =====================================================================
class TestSeguridad(BaseTestCase):
    """Pruebas de seguridad: autenticación, autorización, CSRF."""

    # --- Autenticación ---
    def test_api_tablero_requiere_login(self):
        """API tablero data debe requerir autenticación."""
        res = self.client.get(reverse('api_get_tablero_data'))
        self.assertNotEqual(res.status_code, 200)

    def test_api_asignar_requiere_login(self):
        res = self.client.post(
            reverse('api_asignar_ficha'),
            json.dumps({'ficha_id': 1, 'dia': 'LU', 'hora_id': 1, 'aula_id': 1}),
            content_type='application/json'
        )
        self.assertNotEqual(res.status_code, 200)

    def test_api_generar_requiere_login(self):
        res = self.client.post(
            reverse('api_generar_horario_automatico'),
            json.dumps({'estrategia': '2-2'}),
            content_type='application/json'
        )
        self.assertNotEqual(res.status_code, 200)

    def test_api_limpiar_requiere_login(self):
        res = self.client.post(reverse('api_limpiar_horario'))
        self.assertNotEqual(res.status_code, 200)

    # --- Autorización (rol admin) ---
    def test_estudiante_no_puede_acceder_tablero_data(self):
        """Un estudiante no debe poder acceder al tablero."""
        self.client.login(username='est_test', password='Est123!')
        res = self.client.get(reverse('api_get_tablero_data'))
        self.assertEqual(res.status_code, 403)

    def test_profesor_no_puede_acceder_tablero_data(self):
        """Un profesor no debe poder acceder al tablero."""
        self.client.login(username='prof_test', password='Prof123!')
        res = self.client.get(reverse('api_get_tablero_data'))
        self.assertEqual(res.status_code, 403)

    def test_estudiante_no_puede_crear_asignatura(self):
        self.client.login(username='est_test', password='Est123!')
        res = self.client.post(
            reverse('api_guardar_asignatura'),
            json.dumps({'codigo_asignatura': 'X', 'nombre': 'Hack'}),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 403)

    def test_profesor_no_puede_eliminar_aula(self):
        self.client.login(username='prof_test', password='Prof123!')
        res = self.client.delete(
            reverse('api_eliminar_aula', args=[self.aula.id])
        )
        self.assertEqual(res.status_code, 403)

    def test_estudiante_no_puede_generar_horario(self):
        self.client.login(username='est_test', password='Est123!')
        res = self.client.post(
            reverse('api_generar_horario_automatico'),
            json.dumps({'estrategia': '2-2'}),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 403)

    def test_estudiante_no_puede_limpiar_horario(self):
        self.client.login(username='est_test', password='Est123!')
        res = self.client.post(reverse('api_limpiar_horario'))
        self.assertEqual(res.status_code, 403)

    # --- Validación de entrada ---
    def test_api_aula_capacidad_negativa_rechazada(self):
        """La API debe rechazar capacidad negativa en aulas."""
        self.client.login(username='admin_test', password='Admin123!')
        res = self.client.post(
            reverse('api_guardar_aula'),
            json.dumps({
                'nombre': 'Hack Aula', 'abreviatura': 'HA', 'capacidad': -5
            }),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 400)

    def test_api_aula_capacidad_cero_rechazada(self):
        """La API debe rechazar capacidad cero en aulas."""
        self.client.login(username='admin_test', password='Admin123!')
        res = self.client.post(
            reverse('api_guardar_aula'),
            json.dumps({
                'nombre': 'Zero Aula', 'abreviatura': 'ZA', 'capacidad': 0
            }),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 400)

    def test_api_json_malformado(self):
        """La API debe manejar JSON inválido sin crashear."""
        self.client.login(username='admin_test', password='Admin123!')
        res = self.client.post(
            reverse('api_guardar_asignatura'),
            'esto no es json{{{',
            content_type='application/json'
        )
        self.assertIn(res.status_code, [400, 500])


# =====================================================================
#  4. FIABILIDAD
# =====================================================================
class TestFiabilidad(BaseTestCase):
    """Pruebas de manejo de errores y fiabilidad."""

    def test_eliminar_asignatura_inexistente(self):
        """Eliminar un ID que no existe debe manejar el error."""
        self.client.login(username='admin_test', password='Admin123!')
        res = self.client.delete(
            reverse('api_eliminar_asignatura', args=[99999])
        )
        # No debe crashear (cualquier respuesta controlada es aceptable)
        self.assertIn(res.status_code, [200, 400, 404])

    def test_eliminar_aula_inexistente(self):
        self.client.login(username='admin_test', password='Admin123!')
        res = self.client.delete(
            reverse('api_eliminar_aula', args=[99999])
        )
        self.assertIn(res.status_code, [200, 400, 404])

    def test_asignar_ficha_con_id_inexistente(self):
        """Asignar una ficha inexistente debe retornar error, no crash."""
        self.client.login(username='admin_test', password='Admin123!')
        res = self.client.post(
            reverse('api_asignar_ficha'),
            json.dumps({
                'ficha_id': 99999, 'dia': 'LU',
                'hora_id': self.hora1.id, 'aula_id': self.aula.id
            }),
            content_type='application/json'
        )
        self.assertIn(res.status_code, [200, 400, 404])

    def test_generador_sin_aulas(self):
        """El generador sin aulas debe retornar error graceful."""
        Aula.objects.all().delete()
        success, msg = generar_horario()
        self.assertFalse(success)

    def test_generador_sin_fichas(self):
        """El generador sin fichas debe retornar OK (nada que asignar)."""
        Ficha.objects.all().delete()
        success, msg = generar_horario()
        self.assertTrue(success)

    def test_desasignar_ficha_inexistente(self):
        """Desasignar un ID inexistente no debe crashear."""
        self.client.login(username='admin_test', password='Admin123!')
        res = self.client.post(
            reverse('api_desasignar_ficha'),
            json.dumps({'asignacion_id': 99999}),
            content_type='application/json'
        )
        self.assertIn(res.status_code, [200, 400, 404])

    def test_configuracion_colegio_get_y_post(self):
        """GET y POST del config deben funcionar sin error."""
        self.client.login(username='admin_test', password='Admin123!')
        res = self.client.get(reverse('api_colegio_config'))
        self.assertEqual(res.status_code, 200)

        res = self.client.post(
            reverse('api_colegio_config'),
            json.dumps({
                'nombre': 'Colegio Test', 'anio_lectivo': '2026',
                'periodo': 'Semestre 1'
            }),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)

    def test_doble_asignacion_misma_hora_grado(self):
        """Si el grado ya tiene clase a esa hora, la API debe rechazarla."""
        self.client.login(username='admin_test', password='Admin123!')
        # Asignar la primera
        self.client.post(
            reverse('api_asignar_ficha'),
            json.dumps({
                'ficha_id': self.ficha.id, 'dia': 'LU',
                'hora_id': self.hora1.id, 'aula_id': self.aula.id
            }),
            content_type='application/json'
        )
        # Crear segunda ficha del mismo grado con otra asignatura
        a2 = Asignatura.objects.create(
            codigo_asignatura='ESP2', nombre='Español2',
            abreviatura='ES2', color='#ff0000'
        )
        p2 = Profesor.objects.create(
            codigo_profesor='P-DUP', identificacion='55001',
            primer_nombre='Dup', primer_apellido='Test', abreviatura='DT'
        )
        aula2 = Aula.objects.create(
            nombre='Aula DUP', abreviatura='DUP', capacidad=30
        )
        f2 = Ficha.objects.create(
            profesor=p2, asignatura=a2, grado=self.grado, horas_totales=2
        )
        res = self.client.post(
            reverse('api_asignar_ficha'),
            json.dumps({
                'ficha_id': f2.id, 'dia': 'LU',
                'hora_id': self.hora1.id, 'aula_id': aula2.id
            }),
            content_type='application/json'
        )
        data = res.json()
        self.assertFalse(data.get('success'),
            "La API permitió asignar dos clases al mismo grado y hora")


# =====================================================================
#  5. MANTENIBILIDAD — Análisis Estático
# =====================================================================
class TestMantenibilidad(TestCase):
    """Análisis estático del código fuente."""

    def test_no_debug_prints_en_generador(self):
        """generador.py no debe tener print() de debug."""
        import inspect
        source = inspect.getsource(generar_horario)
        self.assertNotIn('print(', source,
            "generador.py contiene print() de debug que deben eliminarse en producción")

    def test_no_debug_prints_en_views(self):
        """views.py no debe tener print() de debug en producción."""
        import apphorarios.views as views_module
        import inspect
        source = inspect.getsource(views_module)
        count = source.count('print(f"DEBUG')
        # Reportar pero no fallar (es informativo)
        if count > 0:
            self.fail(
                f"views.py contiene {count} sentencias print(f\"DEBUG...\") "
                f"que deberían eliminarse para producción"
            )

    def test_settings_debug_produccion(self):
        """Verificar que DEBUG no está hardcoded en True."""
        from django.conf import settings
        # En test mode Django siempre sobreescribe. Verificamos el archivo.
        import os
        settings_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'Horario', 'settings.py'
        )
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                content = f.read()
            if 'DEBUG = True' in content and 'onrender.com' in content:
                self.fail(
                    "settings.py tiene DEBUG=True junto con host de producción. "
                    "Debe usarse variable de entorno: DEBUG = os.environ.get('DEBUG', 'False') == 'True'"
                )

    def test_secret_key_no_hardcoded(self):
        """Verificar que SECRET_KEY no está hardcoded."""
        import os
        settings_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'Horario', 'settings.py'
        )
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                content = f.read()
            if 'django-insecure' in content:
                self.fail(
                    "settings.py contiene una SECRET_KEY insegura hardcoded. "
                    "Debe usarse variable de entorno: SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback')"
                )

import os
import django
import sys
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Horario.settings')
django.setup()

from apphorarios.models import Asignatura, Profesor, Grado, Hora, Ficha, Aula, FichaAsignada
from apphorarios.generador import generar_horario

def populate():
    print("Borrando datos anteriores...")
    FichaAsignada.objects.all().delete()
    Ficha.objects.all().delete()
    Hora.objects.all().delete()
    Grado.objects.all().delete()
    Profesor.objects.all().delete()
    Asignatura.objects.all().delete()
    Aula.objects.all().delete()

    print("Creando horas (6 periodos por día, 30 horas semanales)...")
    horas_data = [
        (7, 0, 8, 0),
        (8, 0, 9, 0),
        (9, 30, 10, 30),
        (10, 30, 11, 30),
        (11, 30, 12, 30),
        (13, 0, 14, 0),
    ]
    for i, (h1, m1, h2, m2) in enumerate(horas_data):
        Hora.objects.create(
            hora_inicio=datetime.time(h1, m1),
            hora_fin=datetime.time(h2, m2)
        )

    print("Creando asignaturas...")
    asigs = {
        'Matemáticas': Asignatura.objects.create(codigo_asignatura='MAT', nombre='Matemáticas', abreviatura='MAT', color='#3b82f6'),
        'Física': Asignatura.objects.create(codigo_asignatura='FIS', nombre='Física', abreviatura='FIS', color='#2563eb'),
        'Español': Asignatura.objects.create(codigo_asignatura='ESP', nombre='Español y Literatura', abreviatura='ESP', color='#ef4444'),
        'Filosofía': Asignatura.objects.create(codigo_asignatura='FIL', nombre='Filosofía', abreviatura='FIL', color='#b91c1c'),
        'Ciencias': Asignatura.objects.create(codigo_asignatura='CIE', nombre='Ciencias Naturales', abreviatura='CIE', color='#10b981'),
        'Química': Asignatura.objects.create(codigo_asignatura='QUI', nombre='Química', abreviatura='QUI', color='#059669'),
        'Sociales': Asignatura.objects.create(codigo_asignatura='SOC', nombre='Ciencias Sociales', abreviatura='SOC', color='#f59e0b'),
        'Inglés': Asignatura.objects.create(codigo_asignatura='ING', nombre='Inglés', abreviatura='ING', color='#8b5cf6'),
        'Educación Física': Asignatura.objects.create(codigo_asignatura='EFI', nombre='Educación Física', abreviatura='EFI', color='#f97316'),
        'Informática': Asignatura.objects.create(codigo_asignatura='INF', nombre='Informática', abreviatura='INF', color='#64748b'),
        'Artes': Asignatura.objects.create(codigo_asignatura='ART', nombre='Artes', abreviatura='ART', color='#ec4899')
    }

    print("Creando grados...")
    nombres_grados = ['Quinto', 'Sexto', 'Séptimo', 'Octavo', 'Noveno', 'Décimo', 'Once']
    grados = {}
    for g in nombres_grados:
        grados[g] = Grado.objects.create(codigo_grado=g[:3].upper(), nombre=g)

    print("Creando aulas...")
    for g in nombres_grados:
        Aula.objects.create(nombre=f"Aula {g}", abreviatura=f"A-{g[:3].upper()}", capacidad=35)
    Aula.objects.create(nombre="Laboratorio", abreviatura="LAB", capacidad=30)
    Aula.objects.create(nombre="Cancha", abreviatura="CAN", capacidad=50)

    print("Creando profesores...")
    profs = {
        'Carlos': Profesor.objects.create(codigo_profesor='P-CAR', identificacion='1001', primer_nombre='Carlos', primer_apellido='Pérez', abreviatura='CarP'),
        'Laura': Profesor.objects.create(codigo_profesor='P-LAU', identificacion='1002', primer_nombre='Laura', primer_apellido='Gómez', abreviatura='LauG'),
        'María': Profesor.objects.create(codigo_profesor='P-MAR', identificacion='1003', primer_nombre='María', primer_apellido='López', abreviatura='MarL'),
        'Pedro': Profesor.objects.create(codigo_profesor='P-PED', identificacion='1004', primer_nombre='Pedro', primer_apellido='Díaz', abreviatura='PedD'),
        'Ana': Profesor.objects.create(codigo_profesor='P-ANA', identificacion='1005', primer_nombre='Ana', primer_apellido='Ruiz', abreviatura='AnaR'),
        'Luis': Profesor.objects.create(codigo_profesor='P-LUI', identificacion='1006', primer_nombre='Luis', primer_apellido='Mora', abreviatura='LuiM'),
        'Sarah': Profesor.objects.create(codigo_profesor='P-SAR', identificacion='1007', primer_nombre='Sarah', primer_apellido='Smith', abreviatura='SarS'),
        'Kevin': Profesor.objects.create(codigo_profesor='P-KEV', identificacion='1008', primer_nombre='Kevin', primer_apellido='Cruz', abreviatura='KevC'),
        'Jorge': Profesor.objects.create(codigo_profesor='P-JOR', identificacion='1009', primer_nombre='Jorge', primer_apellido='Ríos', abreviatura='JorR'),
        'Rosa': Profesor.objects.create(codigo_profesor='P-ROS', identificacion='1010', primer_nombre='Rosa', primer_apellido='Vega', abreviatura='RosV')
    }

    # Asignaturas al profesor
    profs['Carlos'].asignaturas.add(asigs['Matemáticas'])
    profs['Laura'].asignaturas.add(asigs['Matemáticas'], asigs['Física'])
    profs['María'].asignaturas.add(asigs['Español'])
    profs['Pedro'].asignaturas.add(asigs['Español'], asigs['Filosofía'])
    profs['Ana'].asignaturas.add(asigs['Ciencias'], asigs['Química'])
    profs['Luis'].asignaturas.add(asigs['Sociales'])
    profs['Sarah'].asignaturas.add(asigs['Inglés'])
    profs['Kevin'].asignaturas.add(asigs['Inglés'], asigs['Informática'])
    profs['Jorge'].asignaturas.add(asigs['Educación Física'], asigs['Artes'])
    profs['Rosa'].asignaturas.add(asigs['Química'], asigs['Informática'])

    print("Creando plan de estudios (Fichas)...")
    def crear_ficha(grado_nombre, asig_nombre, prof_nombre, horas):
        Ficha.objects.create(
            grado=grados[grado_nombre],
            asignatura=asigs[asig_nombre],
            profesor=profs[prof_nombre],
            horas_totales=horas
        )

    plan_basico = [
        ('Quinto', [('Matemáticas', 'Carlos', 6), ('Español', 'María', 6), ('Ciencias', 'Ana', 5), ('Sociales', 'Luis', 5), ('Inglés', 'Sarah', 4), ('Educación Física', 'Jorge', 2), ('Informática', 'Kevin', 2)]),
        ('Sexto', [('Matemáticas', 'Carlos', 6), ('Español', 'María', 6), ('Ciencias', 'Ana', 5), ('Sociales', 'Luis', 5), ('Inglés', 'Sarah', 4), ('Educación Física', 'Jorge', 2), ('Artes', 'Jorge', 2)]),
        ('Séptimo', [('Matemáticas', 'Carlos', 6), ('Español', 'María', 6), ('Ciencias', 'Ana', 5), ('Sociales', 'Luis', 5), ('Inglés', 'Sarah', 4), ('Educación Física', 'Jorge', 2), ('Informática', 'Kevin', 2)]),
        ('Octavo', [('Matemáticas', 'Carlos', 5), ('Español', 'María', 5), ('Ciencias', 'Ana', 5), ('Sociales', 'Luis', 5), ('Inglés', 'Sarah', 5), ('Educación Física', 'Jorge', 2), ('Artes', 'Jorge', 3)]),
        ('Noveno', [('Matemáticas', 'Laura', 5), ('Español', 'Pedro', 5), ('Ciencias', 'Ana', 5), ('Sociales', 'Luis', 5), ('Inglés', 'Kevin', 5), ('Educación Física', 'Jorge', 2), ('Informática', 'Rosa', 3)]),
    ]

    plan_media = [
        ('Décimo', [('Matemáticas', 'Laura', 5), ('Física', 'Laura', 3), ('Química', 'Rosa', 3), ('Español', 'Pedro', 4), ('Filosofía', 'Pedro', 3), ('Sociales', 'Luis', 2), ('Inglés', 'Kevin', 5), ('Educación Física', 'Jorge', 2), ('Informática', 'Rosa', 3)]),
        ('Once', [('Matemáticas', 'Laura', 5), ('Física', 'Laura', 3), ('Química', 'Rosa', 3), ('Español', 'Pedro', 4), ('Filosofía', 'Pedro', 3), ('Sociales', 'Luis', 2), ('Inglés', 'Kevin', 5), ('Educación Física', 'Jorge', 2), ('Artes', 'Jorge', 3)]),
    ]

    for grado, materias in plan_basico + plan_media:
        total = sum(h for _, _, h in materias)
        print(f"Grado {grado}: {total} horas semanales (Meta: 30)")
        for asig, prof, h in materias:
            crear_ficha(grado, asig, prof, h)

    print("Generando el horario...")
    success, msg = generar_horario(estrategia='2-1-1')
    if success:
        print("Horario generado con exito!")
    else:
        print("Error al generar horario:", msg)

if __name__ == '__main__':
    populate()

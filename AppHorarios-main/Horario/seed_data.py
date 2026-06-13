import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Horario.settings')
django.setup()

from apphorarios.models import Asignatura, Profesor, Grado, Hora, Aula, Ficha, FichaAsignada

def seed():
    print("Borrando datos antiguos...")
    FichaAsignada.objects.all().delete()
    Ficha.objects.all().delete()
    Asignatura.objects.all().delete()
    Profesor.objects.all().delete()
    Grado.objects.all().delete()
    Hora.objects.all().delete()
    Aula.objects.all().delete()

    print("Creando horas...")
    horas = []
    horarios = [('07:00', '08:00'), ('08:00', '09:00'), ('09:30', '10:30'), ('10:30', '11:15'), ('11:15', '12:00')]
    for h_ini, h_fin in horarios:
        horas.append(Hora.objects.create(hora_inicio=h_ini, hora_fin=h_fin))

    print("Creando aulas...")
    a101 = Aula.objects.create(nombre="Aula 101", capacidad=30)
    a102 = Aula.objects.create(nombre="Aula 102", capacidad=30)
    lab = Aula.objects.create(nombre="Laboratorio de Ciencias", capacidad=25)

    print("Creando grados...")
    g10a = Grado.objects.create(codigo_grado="G10A", nombre="10A", aula_base=a101)
    g10b = Grado.objects.create(codigo_grado="G10B", nombre="10B", aula_base=a102)

    print("Creando asignaturas...")
    mat = Asignatura.objects.create(
        codigo_asignatura="MAT01", nombre="Matemáticas", abreviatura="MAT", color="#E74856"
    )
    cie = Asignatura.objects.create(
        codigo_asignatura="CIE01", nombre="Ciencias Naturales", abreviatura="CIE", color="#107C41"
    )
    his = Asignatura.objects.create(
        codigo_asignatura="HIS01", nombre="Historia Universal", abreviatura="HIS", color="#FFB900"
    )

    print("Creando profesores...")
    prof1 = Profesor.objects.create(
        codigo_profesor="P001", identificacion="1111", primer_nombre="Juan", primer_apellido="Pérez", abreviatura="JP"
    )
    prof1.asignaturas.add(mat, his)

    prof2 = Profesor.objects.create(
        codigo_profesor="P002", identificacion="2222", primer_nombre="María", primer_apellido="Gómez", abreviatura="MG"
    )
    prof2.asignaturas.add(cie, mat)

    print("Creando Fichas (Lecciones/Contratos)...")
    Ficha.objects.create(
        descripcion_ficha="Matemáticas 10A - Prof. Juan",
        horas_totales=4,
        asignatura=mat,
        profesor=prof1,
        grado=g10a
    )
    Ficha.objects.create(
        descripcion_ficha="Historia 10A - Prof. María",
        horas_totales=2,
        asignatura=his,
        profesor=prof2,
        grado=g10a
    )
    Ficha.objects.create(
        descripcion_ficha="Ciencias 10B - Prof. María",
        horas_totales=3,
        asignatura=cie,
        profesor=prof2,
        grado=g10b
    )
    Ficha.objects.create(
        descripcion_ficha="Matemáticas 10B - Prof. Juan",
        horas_totales=4,
        asignatura=mat,
        profesor=prof1,
        grado=g10b
    )

    print("¡Base de datos poblada exitosamente!")

if __name__ == '__main__':
    seed()

from django.http import HttpResponse
from django.shortcuts import render
from .models import Aula, Estudiante, Profesor, Clase, Asignatura, Hora, Grado

def inicio(request):
    return HttpResponse("¡Hola desde mi app Django!")


def lista_estudiantes(request):
    estudiantes = Estudiante.objects.all()
    return render(request, 'mi_app/lista_estudiantes.html', {'estudiantes': estudiantes})


def lista_profesores(request):
    profesores = Profesor.objects.all()
    return render(request, 'mi_app/lista_profesores.html', {'profesores': profesores})


def lista_aulas(request):
    aulas = Aula.objects.all()
    return render(request, 'mi_app/lista_aulas.html', {'aulas': aulas})


def lista_clases(request):
    clases = Clase.objects.all()
    return render(request, 'mi_app/lista_clases.html', {'clases': clases})


def lista_asignaturas(request):
    asignaturas = Asignatura.objects.all()
    return render(request, 'mi_app/lista_asignaturas.html', {'asignaturas': asignaturas})


def lista_horas(request):
    horas = Hora.objects.all()
    return render(request, 'mi_app/lista_horas.html', {'horas': horas})


def lista_grados(request):
    grados = Grado.objects.all()
    return render(request, 'mi_app/lista_grados.html', {'grados': grados})

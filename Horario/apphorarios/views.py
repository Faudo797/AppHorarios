from django.http import HttpResponse
from django.shortcuts import render
from .models import Estudiante
from .models import Profesor
from .models import Aula
from .models import Clase

def inicio(request):
    return HttpResponse("¡Hola desde mi app Django!")

def lista_estudiantes(request):
    estudiantes = Estudiante.objects.all() 
    return render(request, 'mi_app/lista_estudiantes.html', {'estudiantes': estudiantes})

def lista_profesores(request):
    profesores = Profesor.objects.all()  # Obtener todos los profesores
    return render(request, 'mi_app/lista_profesores.html', {'profesores': profesores})

# Vista para mostrar todas las aulas
def lista_aulas(request):
    aulas = Aula.objects.all()  # Obtener todas las aulas
    return render(request, 'mi_app/lista_aulas.html', {'aulas': aulas})

def lista_clases(request):
    clases = Clase.objects.all()
    return render(request, 'clases.html', {'clases': clases})
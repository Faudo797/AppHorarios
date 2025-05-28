from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Aula, Estudiante, Profesor, Clase, Asignatura, Hora, Grado
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django import forms

class LoginForm(AuthenticationForm):
    TIPOS_USUARIO = [
        ('estudiante', 'Estudiante'),
        ('profesor', 'Profesor'),
    ]
    tipo_usuario = forms.ChoiceField(
        choices=TIPOS_USUARIO,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Tipo de Usuario'
    )

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido {username}!')
                return redirect('horario_view')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def horario_view(request):
    # Obtener todos los grados
    grados = Grado.objects.all().order_by('nombre')
    
    # Preparar los datos del horario para cada grado
    grados_con_horario = []
    for grado in grados:
        # Obtener las clases del grado
        clases = Clase.objects.filter(grado=grado)
        horario_grado = {
            'nombre': grado.nombre,
            'horario': {}
        }
        
        # Organizar las clases por día y hora
        for clase in clases:
            dia_hora_key = f"{clase.dia}_{clase.hora}"
            horario_grado['horario'][dia_hora_key] = {
                'materia': clase.asignatura.nombre,
                'materia_abrev': clase.asignatura.codigo_asignatura,
                'materia_clase': clase.asignatura.codigo_asignatura.lower(),
                'profesor': f"{clase.profesor.primer_nombre} {clase.profesor.primer_apellido}"
            }
        
        grados_con_horario.append(horario_grado)

    context = {
        'grados': grados_con_horario,
        'dias': ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'],
        'horas': range(1, 8)  # 7 períodos por día
    }
    
    return render(request, 'horarios/horario_view.html', context)

def dashboard_view(request):
    context = {
        'year': '2024',
        'period': '1',
        'institution_name': 'INSTITUCIÓN EDUCATIVA DEMO'
    }
    return render(request, 'dashboard.html', context)

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

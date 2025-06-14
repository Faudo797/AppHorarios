from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Aula, Estudiante, Profesor, Clase, Asignatura, Hora, Grado
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django import forms
from django.urls import reverse

class LoginForm(AuthenticationForm):
    TIPOS_USUARIO = [
        ('admin', 'Administrador'),
        ('estudiante', 'Estudiante'),
        ('profesor', 'Profesor'),
    ]
    tipo_usuario = forms.ChoiceField(
        choices=TIPOS_USUARIO,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Tipo de Usuario'
    )

class EstudianteForm(forms.ModelForm):
    class Meta:
        model = Estudiante
        fields = ['codigo_estudiante', 'identificacion', 'primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido', 'grado', 'aula']

class ProfesorForm(forms.ModelForm):
    class Meta:
        model = Profesor
        fields = ['codigo_profesor', 'identificacion', 'primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido', 'asignatura', 'aula', 'grado']

class AulaForm(forms.ModelForm):
    class Meta:
        model = Aula
        fields = ['nombre', 'capacidad']

class AsignaturaForm(forms.ModelForm):
    class Meta:
        model = Asignatura
        fields = ['nombre', 'codigo_asignatura']

class GradoForm(forms.ModelForm):
    class Meta:
        model = Grado
        fields = ['nombre']

class HoraForm(forms.ModelForm):
    class Meta:
        model = Hora
        fields = ['hora_inicio', 'hora_fin']

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            tipo_usuario = form.cleaned_data.get('tipo_usuario')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido {username}!')
                
                # Redirigir según el tipo de usuario
                if tipo_usuario == 'admin':
                    return redirect('admin_dashboard')
                else:
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

def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('login')
    
    context = {
        'year': '2024',
        'period': '1',
        'institution_name': 'INSTITUCIÓN EDUCATIVA DEMO'
    }
    return render(request, 'admin/dashboard.html', context)

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

def editar_estudiante(request, estudiante_id):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('login')
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)
    if request.method == 'POST':
        form = EstudianteForm(request.POST, instance=estudiante)
        if form.is_valid():
            form.save()
            messages.success(request, 'Estudiante editado correctamente.')
            return redirect('gestionar_estudiantes')
    else:
        form = EstudianteForm(instance=estudiante)
    return render(request, 'admin/editar_estudiante.html', {'form': form, 'estudiante': estudiante})

def gestionar_estudiantes(request):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('login')
    query = request.GET.get('q', '')
    if query:
        estudiantes = Estudiante.objects.filter(primer_nombre__icontains=query) | Estudiante.objects.filter(primer_apellido__icontains=query) | Estudiante.objects.filter(codigo_estudiante__icontains=query)
    else:
        estudiantes = Estudiante.objects.all()
    if request.method == 'POST':
        form = EstudianteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Estudiante agregado correctamente.')
            return redirect('gestionar_estudiantes')
    else:
        form = EstudianteForm()
    return render(request, 'admin/gestionar_estudiantes.html', {'estudiantes': estudiantes, 'form': form, 'query': query})

def eliminar_estudiante(request, estudiante_id):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('login')
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)
    estudiante.delete()
    messages.success(request, 'Estudiante eliminado correctamente.')
    return redirect('gestionar_estudiantes')

def editar_profesor(request, profesor_id):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('login')
    profesor = get_object_or_404(Profesor, id=profesor_id)
    if request.method == 'POST':
        form = ProfesorForm(request.POST, instance=profesor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profesor editado correctamente.')
            return redirect('gestionar_profesores')
    else:
        form = ProfesorForm(instance=profesor)
    return render(request, 'admin/editar_profesor.html', {'form': form, 'profesor': profesor})

def gestionar_profesores(request):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('login')
    query = request.GET.get('q', '')
    if query:
        profesores = Profesor.objects.filter(primer_nombre__icontains=query) | Profesor.objects.filter(primer_apellido__icontains=query) | Profesor.objects.filter(codigo_profesor__icontains=query)
    else:
        profesores = Profesor.objects.all()
    if request.method == 'POST':
        form = ProfesorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profesor agregado correctamente.')
            return redirect('gestionar_profesores')
    else:
        form = ProfesorForm()
    return render(request, 'admin/gestionar_profesores.html', {'profesores': profesores, 'form': form, 'query': query})

def eliminar_profesor(request, profesor_id):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('login')
    profesor = get_object_or_404(Profesor, id=profesor_id)
    profesor.delete()
    messages.success(request, 'Profesor eliminado correctamente.')
    return redirect('gestionar_profesores')

def editar_aula(request, aula_id):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('login')
    aula = get_object_or_404(Aula, id=aula_id)
    if request.method == 'POST':
        form = AulaForm(request.POST, instance=aula)
        if form.is_valid():
            form.save()
            messages.success(request, 'Aula editada correctamente.')
            return redirect('gestionar_aulas')
    else:
        form = AulaForm(instance=aula)
    return render(request, 'admin/editar_aula.html', {'form': form, 'aula': aula})

def gestionar_aulas(request):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('login')
    query = request.GET.get('q', '')
    if query:
        aulas = Aula.objects.filter(nombre__icontains=query)
    else:
        aulas = Aula.objects.all()
    if request.method == 'POST':
        form = AulaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Aula agregada correctamente.')
            return redirect('gestionar_aulas')
    else:
        form = AulaForm()
    return render(request, 'admin/gestionar_aulas.html', {'aulas': aulas, 'form': form, 'query': query})

def eliminar_aula(request, aula_id):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('login')
    aula = get_object_or_404(Aula, id=aula_id)
    aula.delete()
    messages.success(request, 'Aula eliminada correctamente.')
    return redirect('gestionar_aulas')

def editar_asignatura(request, asignatura_id):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('login')
    asignatura = get_object_or_404(Asignatura, id=asignatura_id)
    if request.method == 'POST':
        form = AsignaturaForm(request.POST, instance=asignatura)
        if form.is_valid():
            form.save()
            messages.success(request, 'Asignatura editada correctamente.')
            return redirect('gestionar_asignaturas')
    else:
        form = AsignaturaForm(instance=asignatura)
    return render(request, 'admin/editar_asignatura.html', {'form': form, 'asignatura': asignatura})

def gestionar_asignaturas(request):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('login')
    query = request.GET.get('q', '')
    if query:
        asignaturas = Asignatura.objects.filter(nombre__icontains=query) | Asignatura.objects.filter(codigo_asignatura__icontains=query)
    else:
        asignaturas = Asignatura.objects.all()
    if request.method == 'POST':
        form = AsignaturaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Asignatura agregada correctamente.')
            return redirect('gestionar_asignaturas')
    else:
        form = AsignaturaForm()
    return render(request, 'admin/gestionar_asignaturas.html', {'asignaturas': asignaturas, 'form': form, 'query': query})

def eliminar_asignatura(request, asignatura_id):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('login')
    asignatura = get_object_or_404(Asignatura, id=asignatura_id)
    asignatura.delete()
    messages.success(request, 'Asignatura eliminada correctamente.')
    return redirect('gestionar_asignaturas')

def editar_grado(request, grado_id):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('login')
    grado = get_object_or_404(Grado, id=grado_id)
    if request.method == 'POST':
        form = GradoForm(request.POST, instance=grado)
        if form.is_valid():
            form.save()
            messages.success(request, 'Grado editado correctamente.')
            return redirect('gestionar_grados')
    else:
        form = GradoForm(instance=grado)
    return render(request, 'admin/editar_grado.html', {'form': form, 'grado': grado})

def gestionar_grados(request):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('login')
    query = request.GET.get('q', '')
    if query:
        grados = Grado.objects.filter(nombre__icontains=query)
    else:
        grados = Grado.objects.all()
    if request.method == 'POST':
        form = GradoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Grado agregado correctamente.')
            return redirect('gestionar_grados')
    else:
        form = GradoForm()
    return render(request, 'admin/gestionar_grados.html', {'grados': grados, 'form': form, 'query': query})

def eliminar_grado(request, grado_id):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('login')
    grado = get_object_or_404(Grado, id=grado_id)
    grado.delete()
    messages.success(request, 'Grado eliminado correctamente.')
    return redirect('gestionar_grados')

def editar_hora(request, hora_id):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('login')
    hora = get_object_or_404(Hora, id=hora_id)
    if request.method == 'POST':
        form = HoraForm(request.POST, instance=hora)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hora editada correctamente.')
            return redirect('gestionar_horas')
    else:
        form = HoraForm(instance=hora)
    return render(request, 'admin/editar_hora.html', {'form': form, 'hora': hora})

def gestionar_horas(request):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('login')
    query = request.GET.get('q', '')
    if query:
        horas = Hora.objects.filter(hora_inicio__icontains=query) | Hora.objects.filter(hora_fin__icontains=query)
    else:
        horas = Hora.objects.all()
    if request.method == 'POST':
        form = HoraForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hora agregada correctamente.')
            return redirect('gestionar_horas')
    else:
        form = HoraForm()
    return render(request, 'admin/gestionar_horas.html', {'horas': horas, 'form': form, 'query': query})

def eliminar_hora(request, hora_id):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('login')
    hora = get_object_or_404(Hora, id=hora_id)
    hora.delete()
    messages.success(request, 'Hora eliminada correctamente.')
    return redirect('gestionar_horas')

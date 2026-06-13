from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
import json
from django.views.decorators.csrf import csrf_exempt
from .models import Aula, Estudiante, Profesor, Ficha, FichaAsignada, Asignatura, Hora, Grado
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django import forms
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from apphorarios.models import Administrador, UsuarioPersonalizado

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
        fields = ['codigo_estudiante', 'identificacion', 'primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido', 'grado']


class ProfesorForm(forms.ModelForm):
    class Meta:
        model = Profesor
        fields = [
            'codigo_profesor','identificacion', 'primer_nombre', 'segundo_nombre', 
            'primer_apellido', 'segundo_apellido', 'asignatura', 'grados'
        ]
        widgets = {
            'grados': forms.CheckboxSelectMultiple(),  # o forms.SelectMultiple()
        }



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

class FichaAsignadaForm(forms.ModelForm):
    class Meta:
        model = FichaAsignada
        fields = ['ficha', 'aula', 'hora', 'dia']
        labels = {
            'ficha': 'Ficha/Lección',
            'aula': 'Aula',
            'hora': 'Hora',
            'dia': 'Día',
        }
        help_texts = {
            'ficha': 'Selecciona la ficha a asignar en este horario.',
        }

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            tipo_usuario = form.cleaned_data.get('tipo_usuario')
            user = authenticate(username=username, password=password)
            
            if user is not None and user.rol == tipo_usuario:
                login(request, user)
                messages.success(request, f'¡Bienvenido {username}!')
                
                # Redirigir según el tipo de usuario
                if user.rol == 'admin':
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
    # Obtener el rol del usuario logueado por defecto
    user_rol = request.user.rol
    user_obj = request.user

    # Verificar si se solicitó un horario específico a través de GET (para el admin)
    # Ahora buscamos por código en lugar de ID
    requested_user_code = request.GET.get('user_code')
    requested_user_type = request.GET.get('user_type')

    print(f"DEBUG: Initial user_rol: {user_rol}, user_obj: {user_obj}")
    print(f"DEBUG: Requested user code: {requested_user_code}, type: {requested_user_type}")

    if request.user.rol == 'admin' and requested_user_code and requested_user_type:
        try:
            if requested_user_type == 'profesor':
                # Buscar profesor por codigo_profesor
                profesor_profile = Profesor.objects.get(codigo_profesor=requested_user_code)
                user_obj = profesor_profile.usuario
                user_rol = 'profesor'
                print(f"DEBUG: Admin viewing professor schedule. Profesor profile: {profesor_profile}, User object: {user_obj}")
            elif requested_user_type == 'estudiante':
                # Buscar estudiante por codigo_estudiante
                estudiante_profile = Estudiante.objects.get(codigo_estudiante=requested_user_code)
                user_obj = estudiante_profile.usuario
                user_rol = 'estudiante'
                print(f"DEBUG: Admin viewing student schedule. Estudiante profile: {estudiante_profile}, User object: {user_obj}")
            else:
                messages.error(request, 'Tipo de usuario no válido.')
                return redirect('admin_dashboard') # O redirigir a ver_horarios
        except (Profesor.DoesNotExist, Estudiante.DoesNotExist) as e:
            messages.error(request, f'Usuario no encontrado con ese código: {e}')
            return redirect('admin_dashboard') # O redirigir a ver_horarios
        
    horario_por_dia = {
        'Lunes': [],
        'Martes': [],
        'Miércoles': [],
        'Jueves': [],
        'Viernes': [],
    }

    print(f"DEBUG: User role for schedule processing: {user_rol}")
    print(f"DEBUG: User object for schedule processing: {user_obj}")

    # Asegurarse de que user_obj tenga un atributo 'profesor_perfil' o 'estudiante_perfil' si el rol lo indica
    if user_rol == 'profesor':
        if hasattr(user_obj, 'profesor_perfil'):
            profesor_obj = user_obj.profesor_perfil
            print(f"DEBUG: Processing professor: {profesor_obj.primer_nombre} {profesor_obj.primer_apellido}")
            clases = FichaAsignada.objects.filter(ficha__profesor=profesor_obj).order_by('hora__hora_inicio', 'dia')
            print(f"DEBUG: Classes found for professor: {clases.count()}")
            for clase in clases:
                dia_str = dict(FichaAsignada.DIAS_SEMANA).get(clase.dia)
                print(f"DEBUG: Class: {clase.ficha.descripcion_ficha}, Dia: {dia_str}, Hora: {clase.hora.hora_inicio}, Grado: {clase.ficha.grado.nombre}, Aula: {clase.aula.nombre}")
                if dia_str:
                    horario_por_dia[dia_str].append({
                        'hora': f"{clase.hora.hora_inicio.strftime('%H:%M')} - {clase.hora.hora_fin.strftime('%H:%M')}",
                        'grado': clase.ficha.grado.nombre,
                        'aula': clase.aula.nombre,
                    })
    elif user_rol == 'estudiante':
        if hasattr(user_obj, 'estudiante_perfil'):
            estudiante_obj = user_obj.estudiante_perfil
            print(f"DEBUG: Processing student: {estudiante_obj.primer_nombre} {estudiante_obj.primer_apellido}")
            clases = FichaAsignada.objects.filter(ficha__grado=estudiante_obj.grado).order_by('hora__hora_inicio', 'dia')
            print(f"DEBUG: Classes found for student: {clases.count()}")
            for clase in clases:
                dia_str = dict(FichaAsignada.DIAS_SEMANA).get(clase.dia)
                print(f"DEBUG: Class: {clase.ficha.descripcion_ficha}, Dia: {dia_str}, Hora: {clase.hora.hora_inicio}, Asignatura: {clase.ficha.asignatura.nombre}, Profesor: {clase.ficha.profesor.primer_nombre}, Aula: {clase.aula.nombre}")
                if dia_str:
                    horario_por_dia[dia_str].append({
                        'hora': f"{clase.hora.hora_inicio.strftime('%H:%M')} - {clase.hora.hora_fin.strftime('%H:%M')}",
                        'asignatura': clase.ficha.asignatura.nombre, 
                        'profesor': f"{clase.ficha.profesor.primer_nombre} {clase.ficha.profesor.primer_apellido}",
                        'aula': clase.aula.nombre,
                    })
    
    print(f"DEBUG: Final horario_por_dia: {horario_por_dia}")
    context = {
        'horario_por_dia': horario_por_dia,
        'dias_semana': ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'],
        'user_rol': user_rol,
    }
    
    return render(request, 'horarios/horario_view.html', context)

def admin_dashboard(request):
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('login')
    
    context = {
        'year': '2025',
        'period': '1',
        'institution_name': 'INSTITUCIÓN EDUCATIVA DEMO'
    }
    return render(request, 'admin/dashboard.html', context)

def dashboard_view(request):
    context = {
        'year': '2025',
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
    clases = FichaAsignada.objects.all()
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
    if request.user.rol != 'admin':
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
    if request.user.rol != 'admin':
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
            estudiante = form.save(commit=False)
            # Crear o actualizar UsuarioPersonalizado para el estudiante
            try:
                usuario_personalizado = UsuarioPersonalizado.objects.get(username=estudiante.codigo_estudiante)
                # Si el usuario ya existe, actualizarlo
                usuario_personalizado.set_password(estudiante.identificacion)
                usuario_personalizado.rol = 'estudiante'
                usuario_personalizado.save()
            except UsuarioPersonalizado.DoesNotExist:
                usuario_personalizado = UsuarioPersonalizado.objects.create_user(
                username=estudiante.codigo_estudiante, 
                password=estudiante.identificacion,
                rol='estudiante'
            )
            
            estudiante.usuario = usuario_personalizado # Vincular el usuario al estudiante
            estudiante.save()
            messages.success(request, 'Estudiante agregado/actualizado correctamente.')
            return redirect('gestionar_estudiantes')
    else:
        form = EstudianteForm()
    return render(request, 'admin/gestionar_estudiantes.html', {'estudiantes': estudiantes, 'form': form, 'query': query})

def eliminar_estudiante(request, estudiante_id):
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('login')
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)
    estudiante.delete()
    messages.success(request, 'Estudiante eliminado correctamente.')
    return redirect('gestionar_estudiantes')

def editar_profesor(request, profesor_id):
    if request.user.rol != 'admin':
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
    if request.user.rol != 'admin':
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
            profesor = form.save(commit=False)
            # Crear o actualizar UsuarioPersonalizado para el profesor
            try:
                usuario_personalizado = UsuarioPersonalizado.objects.get(username=profesor.codigo_profesor)
                usuario_personalizado.set_password(profesor.identificacion)
                usuario_personalizado.rol = 'profesor'
                usuario_personalizado.save()
            except UsuarioPersonalizado.DoesNotExist:
                usuario_personalizado = UsuarioPersonalizado.objects.create_user(
                username=profesor.codigo_profesor, 
                password=profesor.identificacion,
                rol='profesor'
            )
            
            profesor.usuario = usuario_personalizado # Vincular el usuario al profesor
            profesor.save()
            messages.success(request, 'Profesor agregado/actualizado correctamente.')
            return redirect('gestionar_profesores')
    else:
        form = ProfesorForm()
    return render(request, 'admin/gestionar_profesores.html', {'profesores': profesores, 'form': form, 'query': query})

def eliminar_profesor(request, profesor_id):
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('login')
    profesor = get_object_or_404(Profesor, id=profesor_id)
    profesor.delete()
    messages.success(request, 'Profesor eliminado correctamente.')
    return redirect('gestionar_profesores')

def editar_aula(request, aula_id):
    if request.user.rol != 'admin':
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
    if request.user.rol != 'admin':
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
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('login')
    aula = get_object_or_404(Aula, id=aula_id)
    aula.delete()
    messages.success(request, 'Aula eliminada correctamente.')
    return redirect('gestionar_aulas')

def editar_asignatura(request, asignatura_id):
    if request.user.rol != 'admin':
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
    if request.user.rol != 'admin':
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
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('login')
    asignatura = get_object_or_404(Asignatura, id=asignatura_id)
    asignatura.delete()
    messages.success(request, 'Asignatura eliminada correctamente.')
    return redirect('gestionar_asignaturas')

def editar_grado(request, grado_id):
    if request.user.rol != 'admin':
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
    if request.user.rol != 'admin':
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
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('login')
    grado = get_object_or_404(Grado, id=grado_id)
    grado.delete()
    messages.success(request, 'Grado eliminado correctamente.')
    return redirect('gestionar_grados')

def editar_hora(request, hora_id):
    if request.user.rol != 'admin':
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
    if request.user.rol != 'admin':
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
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('login')
    hora = get_object_or_404(Hora, id=hora_id)
    hora.delete()
    messages.success(request, 'Hora eliminada correctamente.')
    return redirect('gestionar_horas')

def gestionar_clases(request):
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('login')
    query = request.GET.get('q', '')
    if query:
        clases = FichaAsignada.objects.filter(ficha__descripcion_ficha__icontains=query)
    else:
        clases = FichaAsignada.objects.all()
    if request.method == 'POST':
        form = FichaAsignadaForm(request.POST)
        if form.is_valid():
            clase = form.save(commit=False)
            clase.save()
            messages.success(request, 'Clase asignada correctamente.')
            return redirect('gestionar_clases')
    else:
        form = FichaAsignadaForm()
    return render(request, 'admin/gestionar_clases.html', {'clases': clases, 'form': form, 'query': query})

def ver_horarios(request):
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('login')
    
    # Ya no necesitamos pasar la lista completa de profesores y estudiantes a la plantilla
    # profesores = Profesor.objects.all().order_by('primer_nombre', 'primer_apellido')
    # estudiantes = Estudiante.objects.all().order_by('primer_nombre', 'primer_apellido')

    selected_user_code = request.GET.get('user_code')
    selected_user_type = request.GET.get('user_type')

    if selected_user_code and selected_user_type:
        return redirect(reverse('horario_view') + f'?user_code={selected_user_code}&user_type={selected_user_type}')

    return render(request, 'admin/ver_horarios.html', {'user_rol': request.user.rol})

@login_required
def tablero_interactivo_view(request):
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('login')
    return render(request, 'admin/tablero_interactivo.html')

@login_required
def api_get_tablero_data(request):
    if request.user.rol != 'admin':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    grados = list(Grado.objects.values('id', 'nombre'))
    horas = list(Hora.objects.values('id', 'hora_inicio', 'hora_fin').order_by('hora_inicio'))
    aulas = list(Aula.objects.values('id', 'nombre'))
    
    fichas = list(Ficha.objects.values(
        'id', 'descripcion_ficha', 'horas_totales', 
        'asignatura__nombre', 'asignatura__abreviatura', 'asignatura__color',
        'profesor__primer_nombre', 'profesor__abreviatura', 'profesor__id',
        'grado__nombre', 'grado__id'
    ))
    
    asignadas = list(FichaAsignada.objects.values(
        'id', 'ficha_id', 'dia', 'hora_id', 'aula_id'
    ))
    
    return JsonResponse({
        'grados': grados,
        'horas': horas,
        'aulas': aulas,
        'fichas': fichas,
        'asignadas': asignadas,
        'dias': [d[0] for d in FichaAsignada.DIAS_SEMANA]
    })

@csrf_exempt
@login_required
def api_asignar_ficha(request):
    if request.user.rol != 'admin':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    if request.method == 'POST':
        data = json.loads(request.body)
        ficha_id = data.get('ficha_id')
        dia = data.get('dia')
        hora_id = data.get('hora_id')
        aula_id = data.get('aula_id')
        
        if FichaAsignada.objects.filter(dia=dia, hora_id=hora_id, aula_id=aula_id).exists():
            return JsonResponse({'success': False, 'error': 'Aula ocupada en esa hora y día.'})
            
        ficha = get_object_or_404(Ficha, id=ficha_id)
        
        if FichaAsignada.objects.filter(dia=dia, hora_id=hora_id, ficha__profesor=ficha.profesor).exists():
            return JsonResponse({'success': False, 'error': 'El profesor ya está ocupado en esa hora.'})

        if FichaAsignada.objects.filter(dia=dia, hora_id=hora_id, ficha__grado=ficha.grado).exists():
            return JsonResponse({'success': False, 'error': 'El grado ya tiene clase en esa hora.'})
            
        asignacion = FichaAsignada.objects.create(
            ficha_id=ficha_id,
            dia=dia,
            hora_id=hora_id,
            aula_id=aula_id
        )
        return JsonResponse({'success': True, 'asignacion_id': asignacion.id})

@csrf_exempt
@login_required
def api_desasignar_ficha(request):
    if request.user.rol != 'admin':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    if request.method == 'POST':
        data = json.loads(request.body)
        asignacion_id = data.get('asignacion_id')
        asignacion = get_object_or_404(FichaAsignada, id=asignacion_id)
        asignacion.delete()
        return JsonResponse({'success': True})

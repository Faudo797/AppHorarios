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

            'ficha': 'Ficha/LecciÃ³n',

            'aula': 'Aula',

            'hora': 'Hora',

            'dia': 'DÃ­a',

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
            
            if user is not None:
                # 🚀 ACCESO DIRECTO SI ES SUPERUSUARIO O MIEMBRO DEL STAFF
                if user.is_superuser or user.is_staff:
                    login(request, user)
                    messages.success(request, f'¡Bienvenido Administrador {username}!')
                    return redirect('admin_dashboard')
                
                # Lógica normal para los usuarios de la institución escolar
                elif user.rol == tipo_usuario:
                    login(request, user)
                    messages.success(request, f'¡Bienvenido {username}!')
                    
                    if user.rol == 'admin':
                        return redirect('admin_dashboard')
                    else:
                        return redirect('horario_view')
                else:
                    messages.error(request, 'Usuario o contraseña incorrectos.')
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



    # Verificar si se solicitÃ³ un horario especÃ­fico a travÃ©s de GET (para el admin)

    # Ahora buscamos por cÃ³digo en lugar de ID

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

                messages.error(request, 'Tipo de usuario no vÃ¡lido.')

                return redirect('admin_dashboard') # O redirigir a ver_horarios

        except (Profesor.DoesNotExist, Estudiante.DoesNotExist) as e:

            messages.error(request, f'Usuario no encontrado con ese cÃ³digo: {e}')

            return redirect('admin_dashboard') # O redirigir a ver_horarios

        

    horario_por_dia = {

        'Lunes': [],

        'Martes': [],

        'MiÃ©rcoles': [],

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

        'dias_semana': ['Lunes', 'Martes', 'MiÃ©rcoles', 'Jueves', 'Viernes'],

        'user_rol': user_rol,

    }

    

    return render(request, 'horarios/horario_view.html', context)



def admin_dashboard(request):
    # 🚀 EXCEPCIÓN: Si es superusuario o staff, o si tiene el rol de admin, lo dejamos pasar
    if request.user.is_superuser or request.user.is_staff or request.user.rol == 'admin':
        context = {
            'year': '2025',
            'period': '1',
            'institution_name': 'INSTITUCIÓN EDUCATIVA DEMO'
        }
        return render(request, 'admin/dashboard.html', context)
    
    # Si no cumple ninguna, se le deniega el acceso
    else:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('login')


def dashboard_view(request):

    context = {

        'year': '2025',

        'period': '1',

        'institution_name': 'INSTITUCIÃN EDUCATIVA DEMO'

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

        messages.error(request, 'No tienes permisos para acceder a esta pÃ¡gina.')

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

        messages.error(request, 'No tienes permisos para acceder a esta pÃ¡gina.')

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

        messages.error(request, 'No tienes permisos para acceder a esta pÃ¡gina.')

        return redirect('login')

    estudiante = get_object_or_404(Estudiante, id=estudiante_id)

    estudiante.delete()

    messages.success(request, 'Estudiante eliminado correctamente.')

    return redirect('gestionar_estudiantes')



def editar_profesor(request, profesor_id):

    if request.user.rol != 'admin':

        messages.error(request, 'No tienes permisos para acceder a esta pÃ¡gina.')

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

        messages.error(request, 'No tienes permisos para acceder a esta pÃ¡gina.')

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

        messages.error(request, 'No tienes permisos para acceder a esta pÃ¡gina.')

        return redirect('login')

    profesor = get_object_or_404(Profesor, id=profesor_id)

    profesor.delete()

    messages.success(request, 'Profesor eliminado correctamente.')

    return redirect('gestionar_profesores')



def editar_aula(request, aula_id):

    if request.user.rol != 'admin':

        messages.error(request, 'No tienes permisos para acceder a esta pÃ¡gina.')

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

        messages.error(request, 'No tienes permisos para acceder a esta pÃ¡gina.')

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

        messages.error(request, 'No tienes permisos para acceder a esta pÃ¡gina.')

        return redirect('login')

    aula = get_object_or_404(Aula, id=aula_id)

    aula.delete()

    messages.success(request, 'Aula eliminada correctamente.')

    return redirect('gestionar_aulas')



def editar_asignatura(request, asignatura_id):

    if request.user.rol != 'admin':

        messages.error(request, 'No tienes permisos para acceder a esta pÃ¡gina.')

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

        messages.error(request, 'No tienes permisos para acceder a esta pÃ¡gina.')

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

        messages.error(request, 'No tienes permisos para acceder a esta pÃ¡gina.')

        return redirect('login')

    asignatura = get_object_or_404(Asignatura, id=asignatura_id)

    asignatura.delete()

    messages.success(request, 'Asignatura eliminada correctamente.')

    return redirect('gestionar_asignaturas')



def editar_grado(request, grado_id):

    if request.user.rol != 'admin':

        messages.error(request, 'No tienes permisos para acceder a esta pÃ¡gina.')

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

        messages.error(request, 'No tienes permisos para acceder a esta pÃ¡gina.')

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

        messages.error(request, 'No tienes permisos para acceder a esta pÃ¡gina.')

        return redirect('login')

    grado = get_object_or_404(Grado, id=grado_id)

    grado.delete()

    messages.success(request, 'Grado eliminado correctamente.')

    return redirect('gestionar_grados')



def editar_hora(request, hora_id):

    if request.user.rol != 'admin':

        messages.error(request, 'No tienes permisos para acceder a esta pÃ¡gina.')

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

        messages.error(request, 'No tienes permisos para acceder a esta pÃ¡gina.')

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

        messages.error(request, 'No tienes permisos para acceder a esta pÃ¡gina.')

        return redirect('login')

    hora = get_object_or_404(Hora, id=hora_id)

    hora.delete()

    messages.success(request, 'Hora eliminada correctamente.')

    return redirect('gestionar_horas')



def gestionar_clases(request):

    if request.user.rol != 'admin':

        messages.error(request, 'No tienes permisos para acceder a esta pÃ¡gina.')

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

        messages.error(request, 'No tienes permisos para acceder a esta pÃ¡gina.')

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

        messages.error(request, 'No tienes permisos para acceder a esta pÃ¡gina.')

        return redirect('login')

    return render(request, 'admin/tablero_interactivo.html')



@login_required

def api_get_tablero_data(request):

    if request.user.rol != 'admin':

        return JsonResponse({'error': 'Unauthorized'}, status=403)

    

    grados = list(Grado.objects.values('id', 'nombre').order_by('id'))

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

    

    profesores_qs = Profesor.objects.prefetch_related('asignaturas').all()
    profesores_list = []
    for p in profesores_qs:
        profesores_list.append({
            'id': p.id,
            'primer_nombre': p.primer_nombre,
            'primer_apellido': p.primer_apellido,
            'abreviatura': p.abreviatura,
            'identificacion': p.identificacion,
            'asignaturas_str': ', '.join([a.nombre for a in p.asignaturas.all()])
        })

    return JsonResponse({
        'dias': [d[0] for d in FichaAsignada.DIAS_SEMANA],
        'horas': horas,
        'grados': grados,
        'aulas': aulas,
        'profesores': profesores_list,
        'asignaturas': list(Asignatura.objects.values('id', 'codigo_asignatura', 'nombre', 'abreviatura', 'color')),
        'fichas': fichas,
        'asignadas': asignadas
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

            return JsonResponse({'success': False, 'error': 'Aula ocupada en esa hora y dÃ­a.'})

            

        ficha = get_object_or_404(Ficha, id=ficha_id)

        

        if FichaAsignada.objects.filter(dia=dia, hora_id=hora_id, ficha__profesor=ficha.profesor).exists():

            return JsonResponse({'success': False, 'error': 'El profesor ya estÃ¡ ocupado en esa hora.'})



        if FichaAsignada.objects.filter(dia=dia, hora_id=hora_id, ficha__grado=ficha.grado).exists():

            return JsonResponse({'success': False, 'error': 'El grado ya tiene clase en esa hora.'})

        # Validar consecutividad y límite diario de la asignatura para el grado
        horas_existentes = FichaAsignada.objects.filter(
            dia=dia,
            ficha__grado=ficha.grado,
            ficha__asignatura=ficha.asignatura
        ).select_related('hora')

        if horas_existentes.exists():
            veces_en_dia = horas_existentes.count()
            if veces_en_dia >= 2:
                return JsonResponse({'success': False, 'error': 'No puedes asignar más de 2 horas al día de la misma asignatura.'})

            todas_horas = list(Hora.objects.all().order_by('hora_inicio'))
            todas_horas_ids = [h.id for h in todas_horas]
            try:
                idx_nueva = todas_horas_ids.index(int(hora_id))
                indices_existentes = [todas_horas_ids.index(h.hora.id) for h in horas_existentes]
                es_consecutiva = any(abs(idx_nueva - idx) == 1 for idx in indices_existentes)
                if not es_consecutiva:
                    return JsonResponse({'success': False, 'error': 'Las clases de la misma asignatura en un día deben ser consecutivas.'})
            except (ValueError, TypeError):
                pass

            

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

from apphorarios.generador import generar_horario

@csrf_exempt
@login_required
def api_generar_horario_automatico(request):
    if request.method == 'POST':
        if request.user.rol != 'admin':
            return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
        
        body = request.body.decode('utf-8')
        estrategia = '2-2'
        if body:
            try:
                data = json.loads(body)
                estrategia = data.get('estrategia', '2-2')
            except:
                pass
        
        from apphorarios.models import FichaAsignada
        FichaAsignada.objects.all().delete()
        
        success, message = generar_horario(estrategia=estrategia)
        return JsonResponse({'success': success, 'message': message})
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)
@login_required
def asc_especificacion_view(request):
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('login')
    return render(request, 'admin/especificacion.html')

@login_required
def api_get_asignaturas(request):
    if request.user.rol != 'admin': return JsonResponse({'error': 'Unauthorized'}, status=403)
    asignaturas = list(Asignatura.objects.values('id', 'codigo_asignatura', 'nombre', 'abreviatura', 'color'))
    return JsonResponse({'asignaturas': asignaturas})

@login_required
def api_get_profesores(request):
    if request.user.rol != 'admin': return JsonResponse({'error': 'Unauthorized'}, status=403)
    profs = Profesor.objects.prefetch_related('asignaturas').all()
    profesores_list = []
    for p in profs:
        asigs = list(p.asignaturas.values_list('nombre', flat=True))
        profesores_list.append({
            'id': p.id,
            'codigo_profesor': p.codigo_profesor,
            'identificacion': p.identificacion,
            'primer_nombre': p.primer_nombre,
            'primer_apellido': p.primer_apellido,
            'abreviatura': p.abreviatura,
            'asignaturas_str': ', '.join(asigs)
        })
    return JsonResponse({'profesores': profesores_list})

@login_required
def api_get_grados(request):
    if request.user.rol != 'admin': return JsonResponse({'error': 'Unauthorized'}, status=403)
    grados = list(Grado.objects.values('id', 'nombre'))
    return JsonResponse({'grados': grados})

@login_required
def api_get_aulas(request):
    if request.user.rol != 'admin': return JsonResponse({'error': 'Unauthorized'}, status=403)
    aulas = list(Aula.objects.values('id', 'nombre', 'abreviatura', 'capacidad'))
    return JsonResponse({'aulas': aulas})

# ==========================================
# CRUD APIs
# ==========================================

import json
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required
def api_guardar_asignatura(request):
    if request.user.rol != 'admin': return JsonResponse({'error': 'Unauthorized'}, status=403)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            asig_id = data.get('id')
            if asig_id:
                asig = Asignatura.objects.get(id=asig_id)
                asig.codigo_asignatura = data.get('codigo_asignatura', asig.codigo_asignatura)
                asig.nombre = data.get('nombre', asig.nombre)
                asig.abreviatura = data.get('abreviatura', asig.abreviatura)
                asig.color = data.get('color', asig.color)
                asig.save()
            else:
                asig = Asignatura.objects.create(
                    codigo_asignatura=data.get('codigo_asignatura'),
                    nombre=data.get('nombre'),
                    abreviatura=data.get('abreviatura', ''),
                    color=data.get('color', '#4f46e5')
                )
            return JsonResponse({'success': True, 'id': asig.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
@login_required
def api_eliminar_asignatura(request, id):
    if request.user.rol != 'admin': return JsonResponse({'error': 'Unauthorized'}, status=403)
    if request.method == 'DELETE':
        try:
            Asignatura.objects.filter(id=id).delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
@login_required
def api_guardar_profesor(request):
    if request.user.rol != 'admin': return JsonResponse({'error': 'Unauthorized'}, status=403)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            prof_id = data.get('id')
            if prof_id:
                prof = Profesor.objects.get(id=prof_id)
                prof.codigo_profesor = data.get('codigo_profesor', prof.codigo_profesor)
                prof.identificacion = data.get('identificacion', prof.identificacion)
                prof.primer_nombre = data.get('primer_nombre', prof.primer_nombre)
                prof.primer_apellido = data.get('primer_apellido', prof.primer_apellido)
                prof.abreviatura = data.get('abreviatura', prof.abreviatura)
                prof.save()
            else:
                prof = Profesor.objects.create(
                    codigo_profesor=data.get('codigo_profesor'),
                    identificacion=data.get('identificacion'),
                    primer_nombre=data.get('primer_nombre'),
                    primer_apellido=data.get('primer_apellido'),
                    abreviatura=data.get('abreviatura', '')
                )
            
            # Manage ManyToMany Asignaturas
            if 'asignaturas' in data:
                # data['asignaturas'] should be a list of IDs
                asig_ids = data['asignaturas']
                prof.asignaturas.set(Asignatura.objects.filter(id__in=asig_ids))
            
            return JsonResponse({'success': True, 'id': prof.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
@login_required
def api_eliminar_profesor(request, id):
    if request.user.rol != 'admin': return JsonResponse({'error': 'Unauthorized'}, status=403)
    if request.method == 'DELETE':
        try:
            Profesor.objects.filter(id=id).delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
@login_required
def api_guardar_grado(request):
    if request.user.rol != 'admin': return JsonResponse({'error': 'Unauthorized'}, status=403)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            grado_id = data.get('id')
            if grado_id:
                grado = Grado.objects.get(id=grado_id)
                grado.codigo_grado = data.get('codigo_grado', grado.codigo_grado)
                grado.nombre = data.get('nombre', grado.nombre)
                grado.save()
            else:
                grado = Grado.objects.create(
                    codigo_grado=data.get('codigo_grado'),
                    nombre=data.get('nombre')
                )
            return JsonResponse({'success': True, 'id': grado.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
@login_required
def api_eliminar_grado(request, id):
    if request.user.rol != 'admin': return JsonResponse({'error': 'Unauthorized'}, status=403)
    if request.method == 'DELETE':
        try:
            Grado.objects.filter(id=id).delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
@login_required
def api_guardar_aula(request):
    if request.user.rol != 'admin': return JsonResponse({'error': 'Unauthorized'}, status=403)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            aula_id = data.get('id')
            if aula_id:
                aula = Aula.objects.get(id=aula_id)
                aula.nombre = data.get('nombre', aula.nombre)
                aula.abreviatura = data.get('abreviatura', aula.abreviatura)
                aula.capacidad = data.get('capacidad', aula.capacidad)
                aula.save()
            else:
                aula = Aula.objects.create(
                    nombre=data.get('nombre'),
                    abreviatura=data.get('abreviatura', ''),
                    capacidad=data.get('capacidad', 30)
                )
            return JsonResponse({'success': True, 'id': aula.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
@login_required
def api_eliminar_aula(request, id):
    if request.user.rol != 'admin': return JsonResponse({'error': 'Unauthorized'}, status=403)
    if request.method == 'DELETE':
        try:
            Aula.objects.filter(id=id).delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
@login_required
def api_guardar_ficha(request):
    if request.user.rol != 'admin': return JsonResponse({'error': 'Unauthorized'}, status=403)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ficha_id = data.get('id')
            if ficha_id:
                ficha = Ficha.objects.get(id=ficha_id)
                ficha.profesor_id = data.get('profesor_id')
                ficha.asignatura_id = data.get('asignatura_id')
                ficha.grado_id = data.get('grado_id')
                ficha.horas_totales = data.get('horas_totales', ficha.horas_totales)
                ficha.save()
            else:
                ficha = Ficha.objects.create(
                    profesor_id=data.get('profesor_id'),
                    asignatura_id=data.get('asignatura_id'),
                    grado_id=data.get('grado_id'),
                    horas_totales=data.get('horas_totales', 1)
                )
            return JsonResponse({'success': True, 'id': ficha.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
@login_required
def api_eliminar_ficha(request, id):
    if request.user.rol != 'admin': return JsonResponse({'error': 'Unauthorized'}, status=403)
    if request.method == 'DELETE':
        try:
            Ficha.objects.filter(id=id).delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
@login_required
def api_limpiar_horario(request):
    if request.user.rol != 'admin': return JsonResponse({'error': 'Unauthorized'}, status=403)
    if request.method == 'POST':
        try:
            # Elimina todas las asignaciones existentes del horario
            FichaAsignada.objects.all().delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def horario_impresion_view(request):
    tipo = request.GET.get('tipo', 'grado')
    obj_id = request.GET.get('id', '')
    
    context = {
        'tipo_inicial': tipo,
        'id_inicial': obj_id
    }
    return render(request, 'admin/horario_impresion.html', context)


@login_required
def api_get_horario_individual(request):
    tipo = request.GET.get('tipo')
    obj_id = request.GET.get('id')
    
    if not tipo or not obj_id:
        return JsonResponse({'error': 'Parámetros inválidos'}, status=400)
        
    horas_objs = list(Hora.objects.all().order_by('hora_inicio'))
    dias = [d[0] for d in FichaAsignada.DIAS_SEMANA]
    
    # Calcular estructura de horas y recreos
    estructura = []
    from datetime import datetime, date
    
    for i, h in enumerate(horas_objs):
        estructura.append({
            'tipo': 'hora',
            'id': h.id,
            'inicio': h.hora_inicio.strftime('%I:%M %p').lower(),
            'fin': h.hora_fin.strftime('%I:%M %p').lower()
        })
        
        # Verificar hueco con la siguiente hora
        if i < len(horas_objs) - 1:
            h_next = horas_objs[i+1]
            dt_fin = datetime.combine(date.today(), h.hora_fin)
            dt_next_inicio = datetime.combine(date.today(), h_next.hora_inicio)
            diff = (dt_next_inicio - dt_fin).total_seconds() / 60
            if diff >= 15: # Si hay 15 mins o más de hueco, es un recreo
                estructura.append({
                    'tipo': 'recreo',
                    'inicio': h.hora_fin.strftime('%I:%M %p').lower(),
                    'fin': h_next.hora_inicio.strftime('%I:%M %p').lower()
                })

    asignaciones = []
    if tipo == 'profesor':
        filtro = {'ficha__profesor_id': obj_id}
    elif tipo == 'grado':
        filtro = {'ficha__grado_id': obj_id}
    else:
        return JsonResponse({'error': 'Tipo no soportado'}, status=400)
        
    for a in FichaAsignada.objects.filter(**filtro).select_related('ficha__asignatura', 'ficha__profesor', 'ficha__grado', 'aula'):
        asignaciones.append({
            'dia': a.dia,
            'hora_id': a.hora_id,
            'asignatura': a.ficha.asignatura.nombre,
            'profesor': a.ficha.profesor.abreviatura or a.ficha.profesor.primer_nombre,
            'grado': a.ficha.grado.nombre,
            'aula': a.aula.nombre if a.aula else 'Sin Aula'
        })
        
    return JsonResponse({
        'estructura': estructura,
        'dias': dias,
        'asignaciones': asignaciones
    })

@csrf_exempt
@login_required
def api_colegio_config(request):
    if request.user.rol != 'admin': return JsonResponse({'error': 'Unauthorized'}, status=403)
    from apphorarios.models import ConfiguracionColegio
    
    config = ConfiguracionColegio.get_config()
    
    if request.method == 'GET':
        return JsonResponse({
            'nombre': config.nombre,
            'anio_lectivo': config.anio_lectivo,
            'periodo': config.periodo
        })
    elif request.method == 'POST':
        try:
            body = request.body.decode('utf-8')
            if body:
                data = json.loads(body)
                config.nombre = data.get('nombre', config.nombre)
                config.anio_lectivo = data.get('anio_lectivo', config.anio_lectivo)
                config.periodo = data.get('periodo', config.periodo)
                config.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
@login_required
def api_guardar_hora(request):
    if request.user.rol != 'admin': return JsonResponse({'error': 'Unauthorized'}, status=403)
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            hora_id = data.get('id')
            
            if hora_id:
                h = Hora.objects.get(id=hora_id)
                h.hora_inicio = data.get('hora_inicio', h.hora_inicio)
                h.hora_fin = data.get('hora_fin', h.hora_fin)
                h.save()
            else:
                h = Hora.objects.create(
                    hora_inicio=data['hora_inicio'],
                    hora_fin=data['hora_fin']
                )
            return JsonResponse({'success': True, 'id': h.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
@login_required
def api_eliminar_hora(request, id):
    if request.user.rol != 'admin': return JsonResponse({'error': 'Unauthorized'}, status=403)
    if request.method == 'DELETE':
        try:
            Hora.objects.filter(id=id).delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


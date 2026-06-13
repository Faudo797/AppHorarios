"""
URL configuration for Horario project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from apphorarios import views
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views # Importar las vistas de autenticación de Django

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_view, name='login'),  # Login como página principal
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'), # URL de cierre de sesión
    path('horario/', login_required(views.horario_view), name='horario_view'),
    path('dashboard/', login_required(views.dashboard_view), name='dashboard'),
    path('admin-dashboard/', login_required(views.admin_dashboard), name='admin_dashboard'),
    path('panel/', login_required(views.admin_dashboard), name='panel_dashboard'),
    # Gestión de estudiantes y profesores
    path('panel/estudiantes/', login_required(views.gestionar_estudiantes), name='gestionar_estudiantes'),
    path('panel/estudiantes/eliminar/<int:estudiante_id>/', login_required(views.eliminar_estudiante), name='eliminar_estudiante'),
    path('panel/estudiantes/editar/<int:estudiante_id>/', login_required(views.editar_estudiante), name='editar_estudiante'),
    path('panel/profesores/', login_required(views.gestionar_profesores), name='gestionar_profesores'),
    path('panel/profesores/eliminar/<int:profesor_id>/', login_required(views.eliminar_profesor), name='eliminar_profesor'),
    path('panel/profesores/editar/<int:profesor_id>/', login_required(views.editar_profesor), name='editar_profesor'),
    path('panel/aulas/', login_required(views.gestionar_aulas), name='gestionar_aulas'),
    path('panel/aulas/eliminar/<int:aula_id>/', login_required(views.eliminar_aula), name='eliminar_aula'),
    path('panel/aulas/editar/<int:aula_id>/', login_required(views.editar_aula), name='editar_aula'),
    path('panel/asignaturas/', login_required(views.gestionar_asignaturas), name='gestionar_asignaturas'),
    path('panel/asignaturas/eliminar/<int:asignatura_id>/', login_required(views.eliminar_asignatura), name='eliminar_asignatura'),
    path('panel/asignaturas/editar/<int:asignatura_id>/', login_required(views.editar_asignatura), name='editar_asignatura'),
    path('panel/grados/', login_required(views.gestionar_grados), name='gestionar_grados'),
    path('panel/grados/eliminar/<int:grado_id>/', login_required(views.eliminar_grado), name='eliminar_grado'),
    path('panel/grados/editar/<int:grado_id>/', login_required(views.editar_grado), name='editar_grado'),
    path('panel/horas/', login_required(views.gestionar_horas), name='gestionar_horas'),
    path('panel/horas/eliminar/<int:hora_id>/', login_required(views.eliminar_hora), name='eliminar_hora'),
    path('panel/horas/editar/<int:hora_id>/', login_required(views.editar_hora), name='editar_hora'),
    # Nuevas rutas para Clases y Ver Horarios
    path('panel/clases/', login_required(views.gestionar_clases), name='gestionar_clases'),
    path('panel/ver-horarios/', login_required(views.ver_horarios), name='ver_horarios'),
    # Rutas existentes
    path('estudiantes/', login_required(views.lista_estudiantes), name='lista_estudiantes'),
    path('profesores/', login_required(views.lista_profesores), name='lista_profesores'),
    path('aulas/', login_required(views.lista_aulas), name='lista_aulas'),
    path('clases/', login_required(views.lista_clases), name='lista_clases'),
    path('asignaturas/', login_required(views.lista_asignaturas), name='lista_asignaturas'),
    path('horas/', login_required(views.lista_horas), name='lista_horas'),
    path('grados/', login_required(views.lista_grados), name='lista_grados'),

    # Tablero Interactivo y aSc
    path('panel/tablero/', login_required(views.tablero_interactivo_view), name='tablero_interactivo'),
    path('panel/especificacion/', login_required(views.asc_especificacion_view), name='asc_especificacion'),
    path('api/fichas/data/', login_required(views.api_get_tablero_data), name='api_get_tablero_data'),
    path('api/fichas/asignar/', login_required(views.api_asignar_ficha), name='api_asignar_ficha'),
    path('api/fichas/desasignar/', login_required(views.api_desasignar_ficha), name='api_desasignar_ficha'),
    path('api/fichas/generar/', login_required(views.api_generar_horario_automatico), name='api_generar_horario_automatico'),
    path('panel/horario-individual/', login_required(views.horario_impresion_view), name='horario_impresion'),
    
    # Nuevas APIs CRUD para la vista aSc Especificación
    path('api/asignaturas/', login_required(views.api_get_asignaturas), name='api_get_asignaturas'),
    path('api/asignaturas/guardar/', login_required(views.api_guardar_asignatura), name='api_guardar_asignatura'),
    path('api/asignaturas/eliminar/<int:id>/', login_required(views.api_eliminar_asignatura), name='api_eliminar_asignatura'),
    
    path('api/profesores/', login_required(views.api_get_profesores), name='api_get_profesores'),
    path('api/profesores/guardar/', login_required(views.api_guardar_profesor), name='api_guardar_profesor'),
    path('api/profesores/eliminar/<int:id>/', login_required(views.api_eliminar_profesor), name='api_eliminar_profesor'),

    path('api/grados/', login_required(views.api_get_grados), name='api_get_grados'),
    path('api/grados/guardar/', login_required(views.api_guardar_grado), name='api_guardar_grado'),
    path('api/grados/eliminar/<int:id>/', login_required(views.api_eliminar_grado), name='api_eliminar_grado'),

    path('api/aulas/', login_required(views.api_get_aulas), name='api_get_aulas'),
    path('api/aulas/guardar/', login_required(views.api_guardar_aula), name='api_guardar_aula'),
    path('api/aulas/eliminar/<int:id>/', login_required(views.api_eliminar_aula), name='api_eliminar_aula'),

    path('api/fichas/guardar/', login_required(views.api_guardar_ficha), name='api_guardar_ficha'),
    path('api/fichas/eliminar/<int:id>/', login_required(views.api_eliminar_ficha), name='api_eliminar_ficha'),
    
    path('api/horario/limpiar/', login_required(views.api_limpiar_horario), name='api_limpiar_horario'),
    path('api/horario/individual/', login_required(views.api_get_horario_individual), name='api_get_horario_individual'),
    
    # Configuracion Colegio y Horas
    path('api/configuracion/', login_required(views.api_colegio_config), name='api_colegio_config'),
    path('api/horas/guardar/', login_required(views.api_guardar_hora), name='api_guardar_hora'),
    path('api/horas/eliminar/<int:id>/', login_required(views.api_eliminar_hora), name='api_eliminar_hora'),
]

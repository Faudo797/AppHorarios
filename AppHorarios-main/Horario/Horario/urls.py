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
]

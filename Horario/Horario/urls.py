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


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.inicio, name='inicio'),
    path('estudiantes/', views.lista_estudiantes, name='lista_estudiantes'),
    path('profesores/', views.lista_profesores, name='lista_profesores'),
    path('aulas/', views.lista_aulas, name='lista_aulas'),
    path('clases/', views.lista_clases, name='lista_clases'),
    path('asignaturas/', views.lista_asignaturas, name='lista_asignaturas'),
    path('horas/', views.lista_horas, name='lista_horas'),
    path('grados/', views.lista_grados, name='lista_grados'),
]

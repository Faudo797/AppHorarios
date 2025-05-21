from django.contrib import admin
from .models import Estudiante, Profesor, Aula, Clase

admin.site.register(Aula)
admin.site.register(Estudiante)
admin.site.register(Profesor)
admin.site.register(Clase)
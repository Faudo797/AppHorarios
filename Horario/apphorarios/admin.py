from django.contrib import admin
from .models import (
    Aula,
    Estudiante,
    Profesor,
    Clase,
    Asignatura,
    Hora,
    Grado
)

admin.site.register(Aula)
admin.site.register(Estudiante)
admin.site.register(Profesor)
admin.site.register(Clase)
admin.site.register(Asignatura)
admin.site.register(Hora)
admin.site.register(Grado)
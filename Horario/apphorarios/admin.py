from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    UsuarioPersonalizado,
    Administrador,
    Aula,
    Estudiante,
    Profesor,
    Clase,
    Asignatura,
    Hora,
    Grado
)

@admin.register(UsuarioPersonalizado)
class UsuarioPersonalizadoAdmin(UserAdmin):
    model = UsuarioPersonalizado
    list_display = ['username', 'email', 'rol', 'is_staff', 'is_active']
    list_filter = ['rol', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('rol', 'estudiante', 'profesor')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('rol', 'estudiante', 'profesor')}),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)


@admin.register(Administrador)
class AdministradorAdmin(admin.ModelAdmin):
    list_display = ['nombre_completo', 'usuario']
    search_fields = ['nombre_completo', 'usuario__username']

admin.site.register(Aula)
admin.site.register(Estudiante)
admin.site.register(Profesor)
admin.site.register(Clase)
admin.site.register(Asignatura)
admin.site.register(Hora)
admin.site.register(Grado)

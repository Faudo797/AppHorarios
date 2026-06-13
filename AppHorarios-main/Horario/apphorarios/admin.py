from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .models import (
    UsuarioPersonalizado,
    Administrador,
    Aula,
    Estudiante,
    Profesor,
    Ficha,
    FichaAsignada,
    Asignatura,
    Hora,
    Grado
)

User = get_user_model()

# ======================
# Admin para UsuarioPersonalizado
# ======================
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

# ======================
# Admin para Administrador
# ======================
@admin.register(Administrador)
class AdministradorAdmin(admin.ModelAdmin):
    list_display = ['nombre_completo', 'usuario']
    search_fields = ['nombre_completo', 'usuario__username']

# ======================
# Estudiante
# ======================
class EstudianteAdminForm(forms.ModelForm):
    contraseña = forms.CharField(
        label='Contraseña del usuario',
        widget=forms.PasswordInput(),
        required=False
    )

    class Meta:
        model = Estudiante
        fields = '__all__'

class EstudianteAdmin(admin.ModelAdmin):
    form = EstudianteAdminForm

    def save_model(self, request, obj, form, change):
        contraseña = form.cleaned_data.get('contraseña')
        if not obj.usuario:
            if contraseña:
                usuario = User.objects.create_user(
                    username=obj.codigo_estudiante,
                    password=contraseña,
                    rol='estudiante'
                )
                obj.usuario = usuario
        else:
            if contraseña:
                obj.usuario.set_password(contraseña)
                obj.usuario.save()
        super().save_model(request, obj, form, change)

admin.site.register(Estudiante, EstudianteAdmin)

# ======================
# Profesor
# ======================
class ProfesorAdminForm(forms.ModelForm):
    contraseña = forms.CharField(
        label='Contraseña del usuario',
        widget=forms.PasswordInput(),
        required=False
    )

    class Meta:
        model = Profesor
        fields = '__all__'

@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
    form = ProfesorAdminForm
    list_display = ('primer_nombre', 'primer_apellido')
    filter_horizontal = ('asignaturas',)

    def save_model(self, request, obj, form, change):
        contraseña = form.cleaned_data.get('contraseña')
        if not obj.usuario:
            if contraseña:
                usuario = User.objects.create_user(
                    username=obj.codigo_profesor,
                    password=contraseña,
                    rol='profesor'
                )
                obj.usuario = usuario
        else:
            if contraseña:
                obj.usuario.set_password(contraseña)
                obj.usuario.save()
        super().save_model(request, obj, form, change)

# ======================
# Resto de modelos
# ======================
admin.site.register(Aula)
admin.site.register(Ficha)
admin.site.register(FichaAsignada)
admin.site.register(Asignatura)
admin.site.register(Hora)
admin.site.register(Grado)

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings  # Para usar AUTH_USER_MODEL
from django.core.validators import MinValueValidator


class UsuarioPersonalizado(AbstractUser):
    ROLES = (
        ('estudiante', 'Estudiante'),
        ('profesor', 'Profesor'),
        ('admin', 'Administrador'),  # Nuevo rol añadido
    )
    rol = models.CharField(max_length=10, choices=ROLES)
    estudiante = models.OneToOneField('Estudiante', null=True, blank=True, on_delete=models.CASCADE)
    profesor = models.OneToOneField('Profesor', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.username} ({self.rol})"


class Administrador(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nombre_completo = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre_completo


class Asignatura(models.Model):
    codigo_asignatura = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100, default='Sin nombre', unique=True)
    abreviatura = models.CharField(max_length=10, default='', blank=True, unique=True)
    color = models.CharField(max_length=7, default='#FFFFFF', help_text="Color en formato HEX (ej. #FF5733)")

    def __str__(self):
        return self.nombre

class Hora(models.Model):
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def __str__(self):
        return f"{self.hora_inicio.strftime('%H:%M')} - {self.hora_fin.strftime('%H:%M')}"



class Grado(models.Model):
    codigo_grado = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100, unique=True)  # Sin choices, para que sea libre
    aula_base = models.ForeignKey('Aula', on_delete=models.SET_NULL, null=True, blank=True, related_name='grados_base', help_text="Aula principal para este grado")

    def __str__(self):
        return self.nombre



class Aula(models.Model):
    nombre = models.CharField(max_length=50, unique=True)  # este es el 'nombre' del formulario
    abreviatura = models.CharField(max_length=10, blank=True, default='', unique=True)
    capacidad = models.IntegerField(default=30, validators=[MinValueValidator(1)])  # capacidad máxima predeterminada

    def __str__(self):
        return f"{self.nombre} (Capacidad: {self.capacidad})"



class Estudiante(models.Model):
    codigo_estudiante = models.CharField(max_length=10, unique=True)
    identificacion = models.CharField(max_length=20, unique=True)
    primer_nombre = models.CharField(max_length=100, default='Nombre')
    segundo_nombre = models.CharField(max_length=100, blank=True, null=True)
    primer_apellido = models.CharField(max_length=100, default='Apellido')
    segundo_apellido = models.CharField(max_length=100, blank=True, null=True)
    grado = models.ForeignKey('Grado', on_delete=models.CASCADE, related_name='estudiantes')
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='estudiante_perfil')

    def __str__(self):
        return f"{self.primer_nombre} {self.primer_apellido}"


class Profesor(models.Model):
    codigo_profesor = models.CharField(max_length=10, unique=True)
    identificacion = models.CharField(max_length=20, unique=True)
    primer_nombre = models.CharField(max_length=100, default='Nombre')
    segundo_nombre = models.CharField(max_length=100, blank=True, null=True)
    primer_apellido = models.CharField(max_length=100, default='Apellido')
    segundo_apellido = models.CharField(max_length=100, blank=True, null=True)
    abreviatura = models.CharField(max_length=10, default='', blank=True, help_text="Ej. JP para Juan Pérez")
    asignaturas = models.ManyToManyField('Asignatura', related_name='profesores', blank=True)
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='profesor_perfil')

    def __str__(self):
        return f"{self.primer_nombre} {self.primer_apellido}"

class DisponibilidadProfesor(models.Model):
    DIAS_SEMANA = [
        ('LU', 'Lunes'),
        ('MA', 'Martes'),
        ('MI', 'Miércoles'),
        ('JU', 'Jueves'),
        ('VI', 'Viernes'),
    ]
    profesor = models.ForeignKey(Profesor, on_delete=models.CASCADE, related_name='disponibilidades')
    dia = models.CharField(max_length=2, choices=DIAS_SEMANA)
    hora = models.ForeignKey('Hora', on_delete=models.CASCADE)
    disponible = models.BooleanField(default=True)

    class Meta:
        unique_together = ['profesor', 'dia', 'hora']

    def __str__(self):
        estado = "Disponible" if self.disponible else "No Disponible"
        return f"{self.profesor} - {self.get_dia_display()} {self.hora}: {estado}"



class Ficha(models.Model):
    descripcion_ficha = models.CharField(max_length=100, default='Ficha sin descripción')
    profesor = models.ForeignKey(Profesor, on_delete=models.CASCADE, related_name='fichas')
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE, related_name='fichas')
    grado = models.ForeignKey(Grado, on_delete=models.CASCADE, related_name='fichas')
    horas_totales = models.IntegerField(default=1, validators=[MinValueValidator(1)], help_text="Cantidad de horas a la semana")

    def __str__(self):
        return f"{self.asignatura.abreviatura or self.asignatura.nombre} - {self.profesor.abreviatura or self.profesor.primer_nombre} ({self.grado.nombre})"

class FichaAsignada(models.Model):
    DIAS_SEMANA = [
        ('LU', 'Lunes'),
        ('MA', 'Martes'),
        ('MI', 'Miércoles'),
        ('JU', 'Jueves'),
        ('VI', 'Viernes'),
    ]
    ficha = models.ForeignKey(Ficha, on_delete=models.CASCADE, related_name='asignaciones')
    dia = models.CharField(max_length=2, choices=DIAS_SEMANA, default='LU')
    hora = models.ForeignKey(Hora, on_delete=models.CASCADE, related_name='fichas_asignadas')
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE, related_name='fichas_asignadas')

    class Meta:
        unique_together = [
            ('aula', 'hora', 'dia'),
        ]

    def __str__(self):
        return f"{self.ficha} -> {self.dia} {self.hora}"

class ConfiguracionColegio(models.Model):
    nombre = models.CharField(max_length=200, default='Institución Educativa Demo')
    anio_lectivo = models.CharField(max_length=20, default='2026')
    periodo = models.CharField(max_length=50, default='Semestre 1')

    def __str__(self):
        return f"{self.nombre} - {self.anio_lectivo}"

    @classmethod
    def get_config(cls):
        config, created = cls.objects.get_or_create(id=1)
        return config

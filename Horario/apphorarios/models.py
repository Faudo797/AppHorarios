from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings  # Para usar AUTH_USER_MODEL


# Usuario personalizado
class UsuarioPersonalizado(AbstractUser):
    ROLES = (
        ('estudiante', 'Estudiante'),
        ('profesor', 'Profesor'),
    )
    rol = models.CharField(max_length=10, choices=ROLES)
    estudiante = models.OneToOneField('Estudiante', null=True, blank=True, on_delete=models.CASCADE)
    profesor = models.OneToOneField('Profesor', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.username} ({self.rol})"


# Administrador
class Administrador(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nombre_completo = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre_completo


# Asignatura
class Asignatura(models.Model):
    codigo_asignatura = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100, default='Sin nombre')

    def __str__(self):
        return self.nombre


# Hora
class Hora(models.Model):
    nombre = models.CharField(max_length=50, default='08:00 - 09:00')
    nombre = models.CharField(max_length=50, default='08:00 - 09:00')  # ✅ ejemplo por defecto
    hora_inicio = models.TimeField(default='08:00')
    hora_fin = models.TimeField(default='09:00')

    def __str__(self):
        return self.nombre


# Grado
class Grado(models.Model):
    codigo_grado = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100, default='Sin grado')

    def __str__(self):
        return self.nombre


# Aula
class Aula(models.Model):
    codigo_aula = models.CharField(max_length=10, unique=True)
    numero_aula = models.CharField(max_length=50, default='Aula 1')
    ubicacion = models.CharField(max_length=100, default='Ubicación desconocida')
    nombre = models.CharField(max_length=100, default='Aula')
    capacidad = models.IntegerField(default=30)
    numero_aula = models.CharField(max_length=50, default='Aula 1')
    ubicacion = models.CharField(max_length=100, default='Ubicación desconocida')

    def __str__(self):
        return f"{self.numero_aula} - {self.ubicacion}"


# Estudiante
class Estudiante(models.Model):
    codigo_estudiante = models.CharField(max_length=10, unique=True)
    identificacion = models.CharField(max_length=20)
    primer_nombre = models.CharField(max_length=100, default='Nombre')
    segundo_nombre = models.CharField(max_length=100, blank=True, null=True)
    primer_apellido = models.CharField(max_length=100, default='Apellido')
    segundo_apellido = models.CharField(max_length=100, blank=True, null=True)
    grado = models.ForeignKey(Grado, on_delete=models.CASCADE, related_name='estudiantes')
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE, related_name='estudiantes')

    def __str__(self):
        return f"{self.primer_nombre} {self.primer_apellido}"


# Profesor
class Profesor(models.Model):
    codigo_profesor = models.CharField(max_length=10, unique=True)
    identificacion = models.CharField(max_length=20)
    primer_nombre = models.CharField(max_length=100, default='Nombre')
    segundo_nombre = models.CharField(max_length=100, blank=True, null=True)
    primer_apellido = models.CharField(max_length=100, default='Apellido')
    segundo_apellido = models.CharField(max_length=100, blank=True, null=True)
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE, related_name='profesores')
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE, related_name='profesores')
    grado = models.ForeignKey(Grado, on_delete=models.CASCADE, related_name='profesores', null=True, blank=True)

    def __str__(self):
        return f"{self.primer_nombre} {self.primer_apellido}"


# Clase (Horario)
class Clase(models.Model):
    descripcion_clase = models.CharField(max_length=100, default='Clase sin descripción')
    profesor = models.ForeignKey(Profesor, on_delete=models.CASCADE, related_name='clases')
    estudiantes = models.ManyToManyField(Estudiante, related_name='clases')
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE, related_name='clases')
    hora = models.ForeignKey(Hora, on_delete=models.CASCADE, related_name='clases')

    DIAS_SEMANA = [
        ('LU', 'Lunes'),
        ('MA', 'Martes'),
        ('MI', 'Miércoles'),
        ('JU', 'Jueves'),
        ('VI', 'Viernes'),
    ]
    dia = models.CharField(max_length=2, choices=DIAS_SEMANA)

    def __str__(self):
        return f"{self.descripcion_clase}"

## Creacion del modelo para login Jhonatan
from django.contrib.auth.models import AbstractUser
from django.db import models

class UsuarioPersonalizado(AbstractUser):
    ROLES = (
        ('estudiante', 'Estudiante'),
        ('profesor', 'Profesor'),
    )
    rol = models.CharField(max_length=10, choices=ROLES)
    estudiante = models.OneToOneField('Estudiante', null=True, blank=True, on_delete=models.CASCADE)
    profesor = models.OneToOneField('Profesor', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.username} ({self.rol})"

    class Meta:
        unique_together = [
            ('aula', 'hora', 'dia'),
            ('profesor', 'hora', 'dia'),
        ]



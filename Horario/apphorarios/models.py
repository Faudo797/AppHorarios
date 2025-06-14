from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings  # Para usar AUTH_USER_MODEL


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
    nombre = models.CharField(max_length=100, default='Sin nombre')

    def __str__(self):
        return self.nombre

class Hora(models.Model):
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def __str__(self):
        return f"{self.hora_inicio.strftime('%H:%M')} - {self.hora_fin.strftime('%H:%M')}"



class Grado(models.Model):
    codigo_grado = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100)  # Sin choices, para que sea libre

    def __str__(self):
        return self.nombre



class Aula(models.Model):
    nombre = models.CharField(max_length=50)  # este es el 'nombre' del formulario
    capacidad = models.IntegerField(default=30)  # capacidad máxima predeterminada

    def __str__(self):
        return f"{self.nombre} (Capacidad: {self.capacidad})"



class Estudiante(models.Model):
    codigo_estudiante = models.CharField(max_length=10, unique=True)
    identificacion = models.CharField(max_length=20)
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
    identificacion = models.CharField(max_length=20)
    primer_nombre = models.CharField(max_length=100, default='Nombre')
    segundo_nombre = models.CharField(max_length=100, blank=True, null=True)
    primer_apellido = models.CharField(max_length=100, default='Apellido')
    segundo_apellido = models.CharField(max_length=100, blank=True, null=True)
    asignatura = models.ForeignKey('Asignatura', on_delete=models.CASCADE, related_name='profesores')
    grados = models.ManyToManyField('Grado', related_name='profesores', blank=True)
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='profesor_perfil')

    def __str__(self):
        return f"{self.primer_nombre} {self.primer_apellido}"



class Clase(models.Model):
    descripcion_clase = models.CharField(max_length=100, default='Clase sin descripción')
    profesor = models.ForeignKey(Profesor, on_delete=models.CASCADE, related_name='clases')
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE, related_name='clases')
    hora = models.ForeignKey(Hora, on_delete=models.CASCADE, related_name='clases')

    DIAS_SEMANA = [
        ('LU', 'Lunes'),
        ('MA', 'Martes'),
        ('MI', 'Miércoles'),
        ('JU', 'Jueves'),
        ('VI', 'Viernes'),
    ]
    dia = models.CharField(max_length=2, choices=DIAS_SEMANA, default='LU')

    grado = models.ForeignKey(Grado, on_delete=models.CASCADE, related_name='clases')

    def estudiantes_asociados(self):
        return self.grado.estudiantes.all()

    def __str__(self):
        return f"{self.descripcion_clase}"

    class Meta:
        unique_together = [
            ('aula', 'hora', 'dia'),
            ('profesor', 'hora', 'dia'),
        ]
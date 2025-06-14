from django.db import models

class Asignatura(models.Model):
    codigo_asignatura = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100, default='Sin nombre')  # ✅ valor por defecto

    def __str__(self):
        return self.nombre


class Hora(models.Model):
    nombre = models.CharField(max_length=50, default='08:00 - 09:00')  # ✅ ejemplo por defecto

    def __str__(self):
        return self.nombre


class Grado(models.Model):
    codigo_grado = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100, default='Sin grado')  # ✅ valor por defecto

    def __str__(self):
        return self.nombre


class Aula(models.Model):
    codigo_aula = models.CharField(max_length=10, unique=True)
    numero_aula = models.CharField(max_length=50, default='Aula 1')  # ✅ ejemplo
    ubicacion = models.CharField(max_length=100, default='Ubicación desconocida')  # ✅ ejemplo

    def __str__(self):
        return f"{self.numero_aula} - {self.ubicacion}"


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


class Clase(models.Model):
    descripcion_clase = models.CharField(max_length=100, default='Clase sin descripción')  # ✅ por si acaso
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

class Meta:
    unique_together = ('aula', 'hora', 'dia')
    unique_together = ('profesor', 'hora', 'dia')

class Administrador(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre_completo = models.CharField(max_length=100)

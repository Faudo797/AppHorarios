from django.db import models

# Nuevos modelos
class Asignatura(models.Model):
    codigo_asignatura = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Hora(models.Model):
    nombre = models.CharField(max_length=50)  # Ejemplo: "08:00 - 09:00"

    def __str__(self):
        return self.nombre


class Grado(models.Model):
    codigo_grado = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


# Modelos existentes con modificaciones
class Aula(models.Model):
    codigo_aula = models.CharField(max_length=10, unique=True)
    numero_aula = models.CharField(max_length=50)
    ubicacion = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.numero_aula} - {self.ubicacion}"


class Estudiante(models.Model):
    codigo_estudiante = models.CharField(max_length=10, unique=True)
    identificacion = models.CharField(max_length=20)
    primer_nombre = models.CharField(max_length=100)
    segundo_nombre = models.CharField(max_length=100, blank=True, null=True)
    primer_apellido = models.CharField(max_length=100)
    segundo_apellido = models.CharField(max_length=100, blank=True, null=True)
    grado = models.ForeignKey(Grado, on_delete=models.CASCADE, related_name='estudiantes')  # Modificado
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE, related_name='estudiantes')

    def __str__(self):
        return f"{self.primer_nombre} {self.primer_apellido}"


class Profesor(models.Model):
    codigo_profesor = models.CharField(max_length=10, unique=True)
    identificacion = models.CharField(max_length=20)
    primer_nombre = models.CharField(max_length=100)
    segundo_nombre = models.CharField(max_length=100, blank=True, null=True)
    primer_apellido = models.CharField(max_length=100)
    segundo_apellido = models.CharField(max_length=100, blank=True, null=True)
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE, related_name='profesores')  # Modificado
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE, related_name='profesores')
    grado = models.ForeignKey(Grado, on_delete=models.CASCADE, related_name='profesores')  # Nuevo

    def __str__(self):
        return f"{self.primer_nombre} {self.primer_apellido}"


class Clase(models.Model):
    descripcion_clase = models.CharField(max_length=100)
    profesor = models.ForeignKey(Profesor, on_delete=models.CASCADE, related_name='clases')
    estudiantes = models.ManyToManyField(Estudiante, related_name='clases')
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE, related_name='clases')
    hora = models.ForeignKey(Hora, on_delete=models.CASCADE, related_name='clases')  # Nuevo

    def __str__(self):
        return f"{self.descripcion_clase}"

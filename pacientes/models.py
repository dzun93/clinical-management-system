from django.db import models

# Create your models here.

class Paciente(models.Model):
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)

    numero_identidad = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Número de identidad"
    )

    fecha_nacimiento = models.DateField()

    telefono = models.CharField(
        max_length=20,
        verbose_name="Teléfono"
    )

    correo_electronico = models.EmailField(
        max_length=150,
        blank=True,
        verbose_name="Correo electrónico"
    )

    direccion = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="Dirección"
    )

    estado_civil = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Estado civil"
    )

    contacto_emergencia = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Contacto de emergencia"
    )

    telefono_emergencia = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Teléfono de emergencia"
    )

    activo = models.BooleanField(default=True)

    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["apellidos", "nombres"]
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models

from pacientes.models import Paciente


class Cita(models.Model):

    class EstadoCita(models.TextChoices):
        PROGRAMADA = "PROGRAMADA", "Programada"
        CONFIRMADA = "CONFIRMADA", "Confirmada"
        COMPLETADA = "COMPLETADA", "Completada"
        CANCELADA = "CANCELADA", "Cancelada"
        NO_ASISTIO = "NO_ASISTIO", "No asistió"

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.PROTECT,
        related_name="citas",
        verbose_name="Paciente"
    )

    fecha_cita = models.DateField(
        verbose_name="Fecha de la cita"
    )

    hora_cita = models.TimeField(
        verbose_name="Hora de la cita"
    )

    motivo = models.CharField(
        max_length=250,
        verbose_name="Motivo de la cita"
    )

    estado = models.CharField(
        max_length=20,
        choices=EstadoCita.choices,
        default=EstadoCita.PROGRAMADA,
        verbose_name="Estado"
    )

    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones"
    )

    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="citas_registradas",
        verbose_name="Registrado por"
    )

    activo = models.BooleanField(
        default=True
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    fecha_actualizacion = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "fecha_cita",
            "hora_cita"
        ]

        verbose_name = "Cita"
        verbose_name_plural = "Citas"

    def __str__(self):
        return (
            f"{self.paciente.nombres} "
            f"{self.paciente.apellidos} - "
            f"{self.fecha_cita:%d/%m/%Y} "
            f"{self.hora_cita:%H:%M}"
        )

    @property
    def codigo_cita(self):
        return f"CIT-{self.id:06d}" if self.id else "CIT-PENDIENTE"
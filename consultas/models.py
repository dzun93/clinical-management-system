from django.conf import settings
from django.db import models
from expedientes.models import ExpedienteClinico


class ConsultaMedica(models.Model):

    expediente = models.ForeignKey(
        ExpedienteClinico,
        on_delete=models.PROTECT,
        related_name="consultas",
        verbose_name="Expediente clínico"
    )

    fecha_consulta = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de consulta"
    )

    motivo_consulta = models.TextField(
        verbose_name="Motivo de consulta"
    )

    sintomas = models.TextField(
        blank=True,
        verbose_name="Síntomas"
    )

    diagnostico = models.TextField(
        verbose_name="Diagnóstico"
    )

    tratamiento = models.TextField(
        blank=True,
        verbose_name="Tratamiento"
    )

    indicaciones = models.TextField(
        blank=True,
        verbose_name="Indicaciones"
    )

    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones"
    )

    proxima_cita = models.DateField(
        null=True,
        blank=True,
        verbose_name="Próxima cita"
    )

    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="consultas_registradas",
        verbose_name="Registrado por"
    )

    activo = models.BooleanField(
        default=True
    )

    fecha_actualizacion = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-fecha_consulta"]
        verbose_name = "Consulta médica"
        verbose_name_plural = "Consultas médicas"

    def __str__(self):
        return (
            f"Consulta de {self.expediente.paciente.nombres} "
            f"{self.expediente.paciente.apellidos} "
            f"- {self.fecha_consulta:%d/%m/%Y}"
        )

    @property
    def codigo_consulta(self):
        return f"CON-{self.id:06d}" if self.id else "CON-PENDIENTE"
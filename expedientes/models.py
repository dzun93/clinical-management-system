from django.db import models
from pacientes.models import Paciente


class ExpedienteClinico(models.Model):

    paciente = models.OneToOneField(
        Paciente,
        on_delete=models.PROTECT,
        related_name="expediente",
        verbose_name="Paciente"
    )

    antecedentes_personales = models.TextField(
        blank=True,
        verbose_name="Antecedentes personales"
    )

    antecedentes_familiares = models.TextField(
        blank=True,
        verbose_name="Antecedentes familiares"
    )

    antecedentes_quirurgicos = models.TextField(
        blank=True,
        verbose_name="Antecedentes quirúrgicos"
    )

    alergias = models.TextField(
        blank=True,
        verbose_name="Alergias"
    )

    fum = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de última menstruación"
    )

    vida_sexual_activa = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Vida sexual activa"
    )

    observaciones_generales = models.TextField(
        blank=True,
        verbose_name="Observaciones generales"
    )

    activo = models.BooleanField(
        default=True
    )

    fecha_apertura = models.DateTimeField(
        auto_now_add=True
    )

    fecha_actualizacion = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Expediente clínico"
        verbose_name_plural = "Expedientes clínicos"

    def __str__(self):
        return f"Expediente de {self.paciente.nombres} {self.paciente.apellidos}"

    @property
    def codigo_expediente(self):
        return f"EXP-{self.id:06d}" if self.id else "EXP-PENDIENTE"
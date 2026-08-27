from django.conf import settings
from django.db import models


class RegistroAuditoria(models.Model):

    class Accion(models.TextChoices):
        INICIAR_SESION = "INICIAR_SESION", "Inicio de sesión"
        CERRAR_SESION = "CERRAR_SESION", "Cierre de sesión"
        CREAR = "CREAR", "Creación"
        EDITAR = "EDITAR", "Edición"
        DESACTIVAR = "DESACTIVAR", "Desactivación"

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="registros_auditoria",
        verbose_name="Usuario"
    )

    accion = models.CharField(
        max_length=20,
        choices=Accion.choices,
        verbose_name="Acción"
    )

    modulo = models.CharField(
        max_length=50,
        verbose_name="Módulo"
    )

    registro = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Registro afectado"
    )

    descripcion = models.TextField(
        verbose_name="Descripción"
    )

    direccion_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Dirección IP"
    )

    fecha_hora = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha y hora"
    )

    class Meta:
        ordering = ["-fecha_hora"]
        verbose_name = "Registro de auditoría"
        verbose_name_plural = "Registros de auditoría"

    def __str__(self):
        usuario = (
            self.usuario.username
            if self.usuario
            else "Usuario no disponible"
        )

        return (
            f"{self.get_accion_display()} - "
            f"{self.modulo} - "
            f"{usuario}"
        )
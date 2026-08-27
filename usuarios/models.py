from django.conf import settings
from django.db import models


class PerfilUsuario(models.Model):

    class Rol(models.TextChoices):
        ADMINISTRADOR = "ADMINISTRADOR", "Administrador"
        DOCTORA = "DOCTORA", "Doctora"
        RECEPCIONISTA = "RECEPCIONISTA", "Recepcionista"

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil",
        verbose_name="Usuario"
    )

    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.RECEPCIONISTA,
        verbose_name="Rol"
    )

    activo = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    fecha_actualizacion = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Perfil de usuario"
        verbose_name_plural = "Perfiles de usuario"

    def __str__(self):
        return f"{self.usuario.username} - {self.get_rol_display()}"

    @property
    def es_administrador(self):
        return self.rol == self.Rol.ADMINISTRADOR

    @property
    def es_doctora(self):
        return self.rol == self.Rol.DOCTORA

    @property
    def es_recepcionista(self):
        return self.rol == self.Rol.RECEPCIONISTA
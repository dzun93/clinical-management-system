from django.contrib import admin
from .models import Paciente

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = (
        "numero_identidad",
        "nombres",
        "apellidos",
        "telefono",
        "activo",
        "fecha_registro",
    )

    search_fields = (
        "numero_identidad",
        "nombres",
        "apellidos",
        "telefono",
    )

    list_filter = (
        "activo",
        "estado_civil",
    )

# Register your models here.

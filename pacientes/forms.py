from django import forms
from .models import Paciente


class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente

        fields = [
            "nombres",
            "apellidos",
            "numero_identidad",
            "fecha_nacimiento",
            "telefono",
            "correo_electronico",
            "direccion",
            "estado_civil",
            "contacto_emergencia",
            "telefono_emergencia",
        ]

        widgets = {
            "fecha_nacimiento": forms.DateInput(
                attrs={"type": "date"}
            ),
        }
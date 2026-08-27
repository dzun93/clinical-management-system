from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Cita


class CitaForm(forms.ModelForm):

    class Meta:
        model = Cita

        fields = [
            "fecha_cita",
            "hora_cita",
            "motivo",
            "estado",
            "observaciones",
        ]

        widgets = {

            "fecha_cita": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "type": "date"
                }
            ),

            "hora_cita": forms.TimeInput(
                format="%H:%M",
                attrs={
                    "type": "time"
                }
            ),

            "motivo": forms.TextInput(
                attrs={
                    "placeholder": "Ej. Control ginecológico, ultrasonido, seguimiento..."
                }
            ),

            "estado": forms.Select(),

            "observaciones": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Información adicional relacionada con la cita..."
                }
            ),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # En una cita nueva, el calendario no permite
        # seleccionar visualmente fechas anteriores a hoy.
        if not self.instance.pk:
            self.fields["fecha_cita"].widget.attrs["min"] = (
                timezone.localdate().isoformat()
            )


    def clean_fecha_cita(self):

        fecha_cita = self.cleaned_data.get("fecha_cita")

        if not fecha_cita:
            return fecha_cita

        hoy = timezone.localdate()

        if fecha_cita < hoy:

            # Si estamos editando una cita antigua,
            # permitimos conservar su fecha original.
            if (
                self.instance.pk
                and self.instance.fecha_cita == fecha_cita
            ):
                return fecha_cita

            raise ValidationError(
                "No se puede programar una cita en una fecha pasada."
            )

        return fecha_cita
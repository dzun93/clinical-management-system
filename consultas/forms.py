from django import forms
from .models import ConsultaMedica


class ConsultaMedicaForm(forms.ModelForm):

    class Meta:
        model = ConsultaMedica

        fields = [
            "motivo_consulta",
            "sintomas",
            "diagnostico",
            "tratamiento",
            "indicaciones",
            "observaciones",
            "proxima_cita",
        ]

        widgets = {
            "motivo_consulta": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Describa el motivo principal de la consulta..."
                }
            ),

            "sintomas": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Registre los síntomas manifestados por la paciente..."
                }
            ),

            "diagnostico": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Registre el diagnóstico médico..."
                }
            ),

            "tratamiento": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Describa el tratamiento indicado..."
                }
            ),

            "indicaciones": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Registre recomendaciones e indicaciones médicas..."
                }
            ),

            "observaciones": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Observaciones adicionales de la consulta..."
                }
            ),

            "proxima_cita": forms.DateInput(
                attrs={
                    "type": "date"
                }
            ),
        }
        
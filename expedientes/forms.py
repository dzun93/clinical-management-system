from django import forms
from .models import ExpedienteClinico


class ExpedienteClinicoForm(forms.ModelForm):

    class Meta:
        model = ExpedienteClinico

        fields = [
            "antecedentes_personales",
            "antecedentes_familiares",
            "antecedentes_quirurgicos",
            "alergias",
            "fum",
            "vida_sexual_activa",
            "observaciones_generales",
        ]

        widgets = {
            "antecedentes_personales": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Describa antecedentes médicos personales relevantes..."
                }
            ),

            "antecedentes_familiares": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Describa antecedentes familiares relevantes..."
                }
            ),

            "antecedentes_quirurgicos": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Cirugías o procedimientos previos..."
                }
            ),

            "alergias": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Medicamentos, alimentos u otras alergias conocidas..."
                }
            ),

            "fum": forms.DateInput(
                attrs={
                    "type": "date"
                }
            ),

            "vida_sexual_activa": forms.Select(
                choices=[
                    ("", "Seleccione..."),
                    (True, "Sí"),
                    (False, "No"),
                ]
            ),

            "observaciones_generales": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Observaciones clínicas adicionales..."
                }
            ),
        }
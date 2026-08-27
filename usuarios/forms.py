from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import PerfilUsuario


User = get_user_model()


class LoginForm(AuthenticationForm):

    username = forms.CharField(
        label="Usuario",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Ingrese su usuario",
                "autocomplete": "username",
            }
        )
    )

    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Ingrese su contraseña",
                "autocomplete": "current-password",
            }
        )
    )


class UsuarioCreacionForm(UserCreationForm):

    first_name = forms.CharField(
        label="Nombres",
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Nombres del usuario"
            }
        )
    )

    last_name = forms.CharField(
        label="Apellidos",
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Apellidos del usuario"
            }
        )
    )

    email = forms.EmailField(
        label="Correo electrónico",
        required=False,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "correo@ejemplo.com"
            }
        )
    )

    rol = forms.ChoiceField(
        label="Rol",
        choices=PerfilUsuario.Rol.choices
    )

    class Meta:
        model = User

        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "rol",
            "password1",
            "password2",
        ]

        widgets = {
            "username": forms.TextInput(
                attrs={
                    "placeholder": "Nombre de usuario"
                }
            ),
        }
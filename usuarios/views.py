from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from django.contrib.auth import get_user_model

from auditoria.models import RegistroAuditoria
from auditoria.utils import registrar_auditoria

from .forms import LoginForm, UsuarioCreacionForm
from .models import PerfilUsuario


User = get_user_model()


def iniciar_sesion(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        formulario = LoginForm(
            request=request,
            data=request.POST
        )

        if formulario.is_valid():

            usuario = formulario.get_user()

            if usuario.is_superuser:

                auth_login(
                    request,
                    usuario
                )

                registrar_auditoria(
                    request=request,
                    accion=RegistroAuditoria.Accion.INICIAR_SESION,
                    modulo="Autenticación",
                    registro=usuario.username,
                    descripcion=(
                        f"El usuario {usuario.username} "
                        f"inició sesión correctamente."
                    )
                )

                return redirect("dashboard")

            try:

                perfil = usuario.perfil

                if not perfil.activo:

                    formulario.add_error(
                        None,
                        "Este usuario se encuentra desactivado."
                    )

                else:

                    auth_login(
                        request,
                        usuario
                    )

                    registrar_auditoria(
                        request=request,
                        accion=RegistroAuditoria.Accion.INICIAR_SESION,
                        modulo="Autenticación",
                        registro=usuario.username,
                        descripcion=(
                            f"El usuario {usuario.username} "
                            f"inició sesión correctamente."
                        )
                    )

                    return redirect("dashboard")

            except PerfilUsuario.DoesNotExist:

                formulario.add_error(
                    None,
                    "El usuario no tiene un perfil asignado."
                )

    else:

        formulario = LoginForm()

    return render(
        request,
        "usuarios/login.html",
        {
            "formulario": formulario,
        }
    )


@require_POST
@login_required
def cerrar_sesion(request):

    usuario = request.user

    registrar_auditoria(
        request=request,
        accion=RegistroAuditoria.Accion.CERRAR_SESION,
        modulo="Autenticación",
        registro=usuario.username,
        descripcion=(
            f"El usuario {usuario.username} "
            f"cerró sesión correctamente."
        )
    )

    auth_logout(request)

    return redirect("login")


def verificar_administrador(usuario):

    if not usuario.is_authenticated:
        return False

    if usuario.is_superuser:
        return True

    try:

        return (
            usuario.perfil.activo
            and usuario.perfil.es_administrador
        )

    except PerfilUsuario.DoesNotExist:

        return False


@login_required
def lista_usuarios(request):

    if not verificar_administrador(request.user):
        raise PermissionDenied

    usuarios = User.objects.select_related(
        "perfil"
    ).order_by(
        "first_name",
        "last_name",
        "username"
    )

    return render(
        request,
        "usuarios/lista_usuarios.html",
        {
            "usuarios": usuarios,
        }
    )


@login_required
def crear_usuario(request):

    if not verificar_administrador(request.user):
        raise PermissionDenied

    if request.method == "POST":

        formulario = UsuarioCreacionForm(
            request.POST
        )

        if formulario.is_valid():

            with transaction.atomic():

                usuario = formulario.save()

                perfil = PerfilUsuario.objects.create(
                    usuario=usuario,
                    rol=formulario.cleaned_data["rol"]
                )

                registrar_auditoria(
                    request=request,
                    accion=RegistroAuditoria.Accion.CREAR,
                    modulo="Usuarios",
                    registro=usuario.username,
                    descripcion=(
                        f"Se creó el usuario {usuario.username} "
                        f"con rol {perfil.get_rol_display()}."
                    )
                )

            return redirect(
                "lista_usuarios"
            )

    else:

        formulario = UsuarioCreacionForm()

    return render(
        request,
        "usuarios/crear_usuario.html",
        {
            "formulario": formulario,
        }
    )
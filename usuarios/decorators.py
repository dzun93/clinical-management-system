from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied

from .models import PerfilUsuario


def roles_permitidos(*roles):

    def decorador(vista):

        @wraps(vista)
        def envoltura(request, *args, **kwargs):

            # Si todavía no inició sesión,
            # lo enviamos al formulario de login.
            if not request.user.is_authenticated:

                return redirect_to_login(
                    request.get_full_path()
                )

            # El superusuario de Django tiene acceso completo.
            if request.user.is_superuser:

                return vista(
                    request,
                    *args,
                    **kwargs
                )

            try:

                perfil = request.user.perfil

            except PerfilUsuario.DoesNotExist:

                raise PermissionDenied

            # Un perfil desactivado no puede acceder.
            if not perfil.activo:

                raise PermissionDenied

            # Comprobamos que el rol esté autorizado.
            if perfil.rol not in roles:

                raise PermissionDenied

            return vista(
                request,
                *args,
                **kwargs
            )

        return envoltura

    return decorador


solo_administrador = roles_permitidos(
    PerfilUsuario.Rol.ADMINISTRADOR
)


administrador_o_doctora = roles_permitidos(
    PerfilUsuario.Rol.ADMINISTRADOR,
    PerfilUsuario.Rol.DOCTORA
)


personal_clinica = roles_permitidos(
    PerfilUsuario.Rol.ADMINISTRADOR,
    PerfilUsuario.Rol.DOCTORA,
    PerfilUsuario.Rol.RECEPCIONISTA
)
from django.urls import path

from . import views


urlpatterns = [
    path(
        "login/",
        views.iniciar_sesion,
        name="login"
    ),

    path(
        "logout/",
        views.cerrar_sesion,
        name="logout"
    ),

    path(
        "",
        views.lista_usuarios,
        name="lista_usuarios"
    ),

    path(
        "nuevo/",
        views.crear_usuario,
        name="crear_usuario"
    ),
]
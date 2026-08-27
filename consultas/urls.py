from django.urls import path
from . import views


urlpatterns = [
    path(
    "",
    views.lista_consultas_global,
    name="lista_consultas_global"
    ),

    path(
        "paciente/<int:paciente_id>/",
        views.lista_consultas,
        name="lista_consultas"
    ),

    path(
        "paciente/<int:paciente_id>/nueva/",
        views.crear_consulta,
        name="crear_consulta"
    ),

    path(
        "paciente/<int:paciente_id>/<int:consulta_id>/",
        views.detalle_consulta,
        name="detalle_consulta"
    ),

    path(
        "paciente/<int:paciente_id>/<int:consulta_id>/editar/",
        views.editar_consulta,
        name="editar_consulta"
    ),
]

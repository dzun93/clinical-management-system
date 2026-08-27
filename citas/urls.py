from django.urls import path
from . import views


urlpatterns = [

    # Agenda general
    path(
        "",
        views.agenda_citas,
        name="agenda_citas"
    ),

    # Citas de una paciente
    path(
        "paciente/<int:paciente_id>/",
        views.lista_citas_paciente,
        name="lista_citas_paciente"
    ),

    # Crear nueva cita para una paciente
    path(
        "paciente/<int:paciente_id>/nueva/",
        views.crear_cita,
        name="crear_cita"
    ),

    # Ver una cita
    path(
        "<int:cita_id>/",
        views.detalle_cita,
        name="detalle_cita"
    ),

    # Editar una cita
    path(
        "<int:cita_id>/editar/",
        views.editar_cita,
        name="editar_cita"
    ),
]
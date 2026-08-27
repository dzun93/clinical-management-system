from django.urls import path
from . import views


urlpatterns = [
    path(
        "paciente/<int:paciente_id>/crear/",
        views.crear_expediente,
        name="crear_expediente"
    ),
    path(
        "paciente/<int:paciente_id>/",
        views.detalle_expediente,
        name="detalle_expediente"
    ),
    path(
        "paciente/<int:paciente_id>/editar/",
        views.editar_expediente,
        name="editar_expediente"
    ),
    
    path("", views.lista_expedientes, name="lista_expedientes"),
]
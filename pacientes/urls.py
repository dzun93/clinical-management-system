from django.urls import path
from . import views

urlpatterns = [
    path("", views.lista_pacientes, name="lista_pacientes"),
    path("nuevo/", views.nuevo_paciente, name="nuevo_paciente"),
    path("<int:paciente_id>/desactivar/",views.desactivar_paciente,name="desactivar_paciente"),
    path("<int:paciente_id>/", views.detalle_paciente, name="detalle_paciente"),
    path("<int:paciente_id>/editar/", views.editar_paciente, name="editar_paciente"),
]
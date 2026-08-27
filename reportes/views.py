from django.shortcuts import render

from pacientes.models import Paciente
from consultas.models import ConsultaMedica
from citas.models import Cita
from usuarios.decorators import administrador_o_doctora


@administrador_o_doctora
def reportes(request):

    # ==========================
    # PACIENTES
    # ==========================

    pacientes = Paciente.objects.filter(
        activo=True
    ).order_by(
        "-fecha_registro"
    )

    total_pacientes = pacientes.count()


    # ==========================
    # CONSULTAS MÉDICAS
    # ==========================

    consultas = ConsultaMedica.objects.filter(
        activo=True
    ).select_related(
        "expediente__paciente"
    ).order_by(
        "-fecha_consulta"
    )

    total_consultas = consultas.count()


    # ==========================
    # CITAS
    # ==========================

    citas = Cita.objects.filter(
        activo=True
    ).select_related(
        "paciente"
    ).order_by(
        "-fecha_cita",
        "-hora_cita"
    )

    total_citas = citas.count()

    citas_programadas = citas.filter(
        estado=Cita.EstadoCita.PROGRAMADA
    ).count()

    citas_confirmadas = citas.filter(
        estado=Cita.EstadoCita.CONFIRMADA
    ).count()

    citas_completadas = citas.filter(
        estado=Cita.EstadoCita.COMPLETADA
    ).count()

    citas_canceladas = citas.filter(
        estado=Cita.EstadoCita.CANCELADA
    ).count()

    citas_no_asistio = citas.filter(
        estado=Cita.EstadoCita.NO_ASISTIO
    ).count()


    # ==========================
    # DATOS PARA LA INTERFAZ
    # ==========================

    return render(
        request,
        "reportes/reportes.html",
        {
            # Indicadores generales
            "total_pacientes": total_pacientes,
            "total_consultas": total_consultas,
            "total_citas": total_citas,

            # Estados de citas
            "citas_programadas": citas_programadas,
            "citas_confirmadas": citas_confirmadas,
            "citas_completadas": citas_completadas,
            "citas_canceladas": citas_canceladas,
            "citas_no_asistio": citas_no_asistio,

            # Registros para tablas
            "pacientes": pacientes[:10],
            "consultas": consultas[:10],
            "citas": citas[:10],
        }
    )
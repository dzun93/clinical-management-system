from django.shortcuts import render
from django.utils import timezone

from pacientes.models import Paciente
from consultas.models import ConsultaMedica
from citas.models import Cita

from usuarios.decorators import personal_clinica

@personal_clinica
def dashboard(request):

    hoy = timezone.localdate()

    # ==========================
    # INDICADORES PRINCIPALES
    # ==========================

    total_pacientes = Paciente.objects.filter(
        activo=True
    ).count()

    total_consultas = ConsultaMedica.objects.filter(
        activo=True
    ).count()

    citas_hoy = Cita.objects.filter(
        activo=True,
        fecha_cita=hoy
    ).exclude(
        estado=Cita.EstadoCita.CANCELADA
    ).count()


    # ==========================
    # PRÓXIMAS CITAS
    # ==========================

    proximas_citas = Cita.objects.filter(
        activo=True,
        fecha_cita__gte=hoy
    ).exclude(
        estado=Cita.EstadoCita.CANCELADA
    ).select_related(
        "paciente"
    ).order_by(
        "fecha_cita",
        "hora_cita"
    )[:5]


    # ==========================
    # CONSULTAS RECIENTES
    # ==========================

    consultas_recientes = ConsultaMedica.objects.filter(
        activo=True
    ).select_related(
        "expediente__paciente"
    ).order_by(
        "-fecha_consulta"
    )[:5]


    return render(
        request,
        "dashboard/dashboard.html",
        {
            "total_pacientes": total_pacientes,
            "total_consultas": total_consultas,
            "citas_hoy": citas_hoy,
            "proximas_citas": proximas_citas,
            "consultas_recientes": consultas_recientes,
            "hoy": hoy,
        }
    )
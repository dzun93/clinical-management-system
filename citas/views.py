from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from pacientes.models import Paciente
from usuarios.decorators import personal_clinica

from auditoria.models import RegistroAuditoria
from auditoria.utils import registrar_auditoria

from .models import Cita
from .forms import CitaForm


@personal_clinica
def agenda_citas(request):

    hoy = timezone.localdate()

    # QuerySet base: todas las citas activas.
    # Los contadores se calculan siempre sobre este conjunto.
    citas_base = Cita.objects.filter(
        activo=True
    ).select_related(
        "paciente"
    )

    # ==========================
    # CONTADORES GENERALES
    # ==========================

    total_citas = citas_base.count()

    citas_programadas = citas_base.filter(
        estado=Cita.EstadoCita.PROGRAMADA
    ).count()

    citas_confirmadas = citas_base.filter(
        estado=Cita.EstadoCita.CONFIRMADA
    ).count()

    citas_hoy = citas_base.filter(
        fecha_cita=hoy
    ).exclude(
        estado=Cita.EstadoCita.CANCELADA
    ).count()


    # ==========================
    # FILTROS DE LA AGENDA
    # ==========================

    estado_filtro = request.GET.get(
        "estado",
        ""
    )

    fecha_filtro = request.GET.get(
        "fecha",
        ""
    )

    citas = citas_base


    # FILTRO POR ESTADO

    estados_validos = [
        Cita.EstadoCita.PROGRAMADA,
        Cita.EstadoCita.CONFIRMADA,
        Cita.EstadoCita.COMPLETADA,
        Cita.EstadoCita.CANCELADA,
        Cita.EstadoCita.NO_ASISTIO,
    ]

    if estado_filtro in estados_validos:

        citas = citas.filter(
            estado=estado_filtro
        )


    # FILTRO POR FECHA

    if fecha_filtro:

        try:

            fecha_convertida = datetime.strptime(
                fecha_filtro,
                "%Y-%m-%d"
            ).date()

            citas = citas.filter(
                fecha_cita=fecha_convertida
            )

        except ValueError:

            fecha_filtro = ""


    return render(
        request,
        "citas/agenda_citas.html",
        {
            "citas": citas,

            "total_citas": total_citas,
            "citas_programadas": citas_programadas,
            "citas_confirmadas": citas_confirmadas,
            "citas_hoy": citas_hoy,

            "hoy": hoy,

            "estado_filtro": estado_filtro,
            "fecha_filtro": fecha_filtro,
        }
    )


@personal_clinica
def lista_citas_paciente(request, paciente_id):

    paciente = get_object_or_404(
        Paciente,
        id=paciente_id,
        activo=True
    )

    citas = Cita.objects.filter(
        paciente=paciente,
        activo=True
    )

    return render(
        request,
        "citas/lista_citas_paciente.html",
        {
            "paciente": paciente,
            "citas": citas,
        }
    )


@personal_clinica
def crear_cita(request, paciente_id):

    paciente = get_object_or_404(
        Paciente,
        id=paciente_id,
        activo=True
    )

    if request.method == "POST":

        formulario = CitaForm(request.POST)

        if formulario.is_valid():

            cita = formulario.save(commit=False)

            cita.paciente = paciente

            if request.user.is_authenticated:
                cita.registrado_por = request.user

            cita.save()

            registrar_auditoria(
                request=request,
                accion=RegistroAuditoria.Accion.CREAR,
                modulo="Citas",
                registro=cita.codigo_cita,
                descripcion=(
                    f"Se registró una nueva cita para la paciente "
                    f"{paciente.nombres} {paciente.apellidos}."
                )
            )

            return redirect(
                "detalle_cita",
                cita_id=cita.id
            )

    else:

        formulario = CitaForm()

    return render(
        request,
        "citas/crear_cita.html",
        {
            "formulario": formulario,
            "paciente": paciente,
        }
    )


@personal_clinica
def detalle_cita(request, cita_id):

    cita = get_object_or_404(
        Cita.objects.select_related("paciente"),
        id=cita_id,
        activo=True
    )

    paciente = cita.paciente

    return render(
        request,
        "citas/detalle_cita.html",
        {
            "cita": cita,
            "paciente": paciente,
        }
    )


@personal_clinica
def editar_cita(request, cita_id):

    cita = get_object_or_404(
        Cita.objects.select_related("paciente"),
        id=cita_id,
        activo=True
    )

    paciente = cita.paciente

    if request.method == "POST":

        formulario = CitaForm(
            request.POST,
            instance=cita
        )

        if formulario.is_valid():

            cita = formulario.save()

            registrar_auditoria(
                request=request,
                accion=RegistroAuditoria.Accion.EDITAR,
                modulo="Citas",
                registro=cita.codigo_cita,
                descripcion=(
                    f"Se actualizó la cita de la paciente "
                    f"{paciente.nombres} {paciente.apellidos}."
                )
            )

            return redirect(
                "detalle_cita",
                cita_id=cita.id
            )

    else:

        formulario = CitaForm(
            instance=cita
        )

    return render(
        request,
        "citas/editar_cita.html",
        {
            "formulario": formulario,
            "cita": cita,
            "paciente": paciente,
        }
    )
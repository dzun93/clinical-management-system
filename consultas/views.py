from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q

from pacientes.models import Paciente
from expedientes.models import ExpedienteClinico
from usuarios.decorators import administrador_o_doctora

from auditoria.models import RegistroAuditoria
from auditoria.utils import registrar_auditoria

from .models import ConsultaMedica
from .forms import ConsultaMedicaForm


@administrador_o_doctora
def lista_consultas_global(request):

    busqueda = request.GET.get("q", "").strip()

    consultas = ConsultaMedica.objects.filter(
        activo=True,
        expediente__activo=True,
        expediente__paciente__activo=True
    ).select_related(
        "expediente__paciente"
    ).order_by(
        "-fecha_consulta"
    )

    if busqueda:
        consultas = consultas.filter(
            Q(expediente__paciente__nombres__icontains=busqueda) |
            Q(expediente__paciente__apellidos__icontains=busqueda) |
            Q(expediente__paciente__numero_identidad__icontains=busqueda) |
            Q(motivo_consulta__icontains=busqueda) |
            Q(diagnostico__icontains=busqueda)
        )

    return render(
        request,
        "consultas/lista_consultas_global.html",
        {
            "consultas": consultas,
            "busqueda": busqueda,
        }
    )


@administrador_o_doctora
def lista_consultas(request, paciente_id):
    paciente = get_object_or_404(
        Paciente,
        id=paciente_id,
        activo=True
    )

    expediente = get_object_or_404(
        ExpedienteClinico,
        paciente=paciente,
        activo=True
    )

    consultas = ConsultaMedica.objects.filter(
        expediente=expediente,
        activo=True
    )

    return render(
        request,
        "consultas/lista_consultas.html",
        {
            "paciente": paciente,
            "expediente": expediente,
            "consultas": consultas,
        }
    )


@administrador_o_doctora
def crear_consulta(request, paciente_id):
    paciente = get_object_or_404(
        Paciente,
        id=paciente_id,
        activo=True
    )

    expediente = get_object_or_404(
        ExpedienteClinico,
        paciente=paciente,
        activo=True
    )

    if request.method == "POST":

        formulario = ConsultaMedicaForm(request.POST)

        if formulario.is_valid():

            consulta = formulario.save(commit=False)

            consulta.expediente = expediente

            if request.user.is_authenticated:
                consulta.registrado_por = request.user

            consulta.save()

            registrar_auditoria(
                request=request,
                accion=RegistroAuditoria.Accion.CREAR,
                modulo="Consultas Médicas",
                registro=consulta.codigo_consulta,
                descripcion=(
                    f"Se registró una nueva consulta médica para la paciente "
                    f"{paciente.nombres} {paciente.apellidos}."
                )
            )

            return redirect(
                "detalle_consulta",
                paciente_id=paciente.id,
                consulta_id=consulta.id
            )

    else:
        formulario = ConsultaMedicaForm()

    return render(
        request,
        "consultas/crear_consulta.html",
        {
            "formulario": formulario,
            "paciente": paciente,
            "expediente": expediente,
        }
    )


@administrador_o_doctora
def detalle_consulta(request, paciente_id, consulta_id):
    paciente = get_object_or_404(
        Paciente,
        id=paciente_id,
        activo=True
    )

    expediente = get_object_or_404(
        ExpedienteClinico,
        paciente=paciente,
        activo=True
    )

    consulta = get_object_or_404(
        ConsultaMedica,
        id=consulta_id,
        expediente=expediente,
        activo=True
    )

    return render(
        request,
        "consultas/detalle_consulta.html",
        {
            "paciente": paciente,
            "expediente": expediente,
            "consulta": consulta,
        }
    )


@administrador_o_doctora
def editar_consulta(request, paciente_id, consulta_id):
    paciente = get_object_or_404(
        Paciente,
        id=paciente_id,
        activo=True
    )

    expediente = get_object_or_404(
        ExpedienteClinico,
        paciente=paciente,
        activo=True
    )

    consulta = get_object_or_404(
        ConsultaMedica,
        id=consulta_id,
        expediente=expediente,
        activo=True
    )

    if request.method == "POST":

        formulario = ConsultaMedicaForm(
            request.POST,
            instance=consulta
        )

        if formulario.is_valid():

            consulta = formulario.save()

            registrar_auditoria(
                request=request,
                accion=RegistroAuditoria.Accion.EDITAR,
                modulo="Consultas Médicas",
                registro=consulta.codigo_consulta,
                descripcion=(
                    f"Se actualizó la consulta médica de la paciente "
                    f"{paciente.nombres} {paciente.apellidos}."
                )
            )

            return redirect(
                "detalle_consulta",
                paciente_id=paciente.id,
                consulta_id=consulta.id
            )

    else:

        formulario = ConsultaMedicaForm(
            instance=consulta
        )

    return render(
        request,
        "consultas/editar_consulta.html",
        {
            "formulario": formulario,
            "paciente": paciente,
            "expediente": expediente,
            "consulta": consulta,
        }
    )
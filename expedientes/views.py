from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q

from pacientes.models import Paciente
from usuarios.decorators import administrador_o_doctora

from auditoria.models import RegistroAuditoria
from auditoria.utils import registrar_auditoria

from .models import ExpedienteClinico
from .forms import ExpedienteClinicoForm


@administrador_o_doctora
def lista_expedientes(request):

    busqueda = request.GET.get("q", "").strip()

    expedientes = ExpedienteClinico.objects.filter(
        activo=True,
        paciente__activo=True
    ).select_related(
        "paciente"
    ).order_by(
        "paciente__apellidos",
        "paciente__nombres"
    )

    if busqueda:
        expedientes = expedientes.filter(
            Q(paciente__nombres__icontains=busqueda) |
            Q(paciente__apellidos__icontains=busqueda) |
            Q(paciente__numero_identidad__icontains=busqueda)
        )

    return render(
        request,
        "expedientes/lista_expedientes.html",
        {
            "expedientes": expedientes,
            "busqueda": busqueda,
        }
    )


@administrador_o_doctora
def crear_expediente(request, paciente_id):
    paciente = get_object_or_404(
        Paciente,
        id=paciente_id,
        activo=True
    )

    # Evita crear un segundo expediente para la misma paciente
    expediente_existente = ExpedienteClinico.objects.filter(
        paciente=paciente
    ).first()

    if expediente_existente:
        return redirect(
            "detalle_expediente",
            paciente_id=paciente.id
        )

    if request.method == "POST":
        formulario = ExpedienteClinicoForm(request.POST)

        if formulario.is_valid():
            expediente = formulario.save(commit=False)
            expediente.paciente = paciente
            expediente.save()

            registrar_auditoria(
                request=request,
                accion=RegistroAuditoria.Accion.CREAR,
                modulo="Expedientes Clínicos",
                registro=expediente.codigo_expediente,
                descripcion=(
                    f"Se creó el expediente clínico de la paciente "
                    f"{paciente.nombres} {paciente.apellidos}."
                )
            )

            return redirect(
                "detalle_expediente",
                paciente_id=paciente.id
            )

    else:
        formulario = ExpedienteClinicoForm()

    return render(
        request,
        "expedientes/crear_expediente.html",
        {
            "formulario": formulario,
            "paciente": paciente,
        }
    )


@administrador_o_doctora
def detalle_expediente(request, paciente_id):
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

    return render(
        request,
        "expedientes/detalle_expediente.html",
        {
            "paciente": paciente,
            "expediente": expediente,
        }
    )


@administrador_o_doctora
def editar_expediente(request, paciente_id):
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
        formulario = ExpedienteClinicoForm(
            request.POST,
            instance=expediente
        )

        if formulario.is_valid():
            expediente = formulario.save()

            registrar_auditoria(
                request=request,
                accion=RegistroAuditoria.Accion.EDITAR,
                modulo="Expedientes Clínicos",
                registro=expediente.codigo_expediente,
                descripcion=(
                    f"Se actualizó el expediente clínico de la paciente "
                    f"{paciente.nombres} {paciente.apellidos}."
                )
            )

            return redirect(
                "detalle_expediente",
                paciente_id=paciente.id
            )

    else:
        formulario = ExpedienteClinicoForm(
            instance=expediente
        )

    return render(
        request,
        "expedientes/editar_expediente.html",
        {
            "formulario": formulario,
            "paciente": paciente,
            "expediente": expediente,
        }
    )
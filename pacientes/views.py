from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from usuarios.decorators import personal_clinica

from .models import Paciente
from .forms import PacienteForm

from auditoria.models import RegistroAuditoria
from auditoria.utils import registrar_auditoria


@personal_clinica
def lista_pacientes(request):
    pacientes = Paciente.objects.filter(activo=True)

    return render(
        request,
        "pacientes/lista_pacientes.html",
        {"pacientes": pacientes}
    )


@personal_clinica
def nuevo_paciente(request):
    if request.method == "POST":
        formulario = PacienteForm(request.POST)

        if formulario.is_valid():
            paciente = formulario.save()

            registrar_auditoria(
                request=request,
                accion=RegistroAuditoria.Accion.CREAR,
                modulo="Pacientes",
                registro=f"PAC-{paciente.id:06d}",
                descripcion=(
                    f"Se registró a la paciente "
                    f"{paciente.nombres} {paciente.apellidos}."
                )
            )

            return redirect("lista_pacientes")

    else:
        formulario = PacienteForm()

    return render(
        request,
        "pacientes/nuevo_paciente.html",
        {"formulario": formulario}
    )


@personal_clinica
def detalle_paciente(request, paciente_id):
    paciente = get_object_or_404(
        Paciente,
        id=paciente_id,
        activo=True
    )

    return render(
        request,
        "pacientes/detalle_paciente.html",
        {"paciente": paciente}
    )


@personal_clinica
def editar_paciente(request, paciente_id):
    paciente = get_object_or_404(
        Paciente,
        id=paciente_id,
        activo=True
    )

    if request.method == "POST":
        formulario = PacienteForm(
            request.POST,
            instance=paciente
        )

        if formulario.is_valid():
            paciente = formulario.save()

            registrar_auditoria(
                request=request,
                accion=RegistroAuditoria.Accion.EDITAR,
                modulo="Pacientes",
                registro=f"PAC-{paciente.id:06d}",
                descripcion=(
                    f"Se actualizaron los datos de la paciente "
                    f"{paciente.nombres} {paciente.apellidos}."
                )
            )

            return redirect(
                "detalle_paciente",
                paciente_id=paciente.id
            )

    else:
        formulario = PacienteForm(
            instance=paciente
        )

    return render(
        request,
        "pacientes/editar_paciente.html",
        {
            "formulario": formulario,
            "paciente": paciente
        }
    )


@personal_clinica
@require_POST
def desactivar_paciente(request, paciente_id):
    paciente = get_object_or_404(
        Paciente,
        id=paciente_id,
        activo=True
    )

    paciente.activo = False
    paciente.save()

    registrar_auditoria(
        request=request,
        accion=RegistroAuditoria.Accion.DESACTIVAR,
        modulo="Pacientes",
        registro=f"PAC-{paciente.id:06d}",
        descripcion=(
            f"Se desactivó a la paciente "
            f"{paciente.nombres} {paciente.apellidos}."
        )
    )

    return redirect("lista_pacientes")
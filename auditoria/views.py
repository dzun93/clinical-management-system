from django.db.models import Q
from django.shortcuts import render

from usuarios.decorators import solo_administrador

from .models import RegistroAuditoria


@solo_administrador
def lista_auditoria(request):

    registros = RegistroAuditoria.objects.select_related(
        "usuario"
    ).order_by(
        "-fecha_hora"
    )

    # ==========================
    # FILTROS
    # ==========================

    busqueda = request.GET.get("q", "").strip()
    accion_filtro = request.GET.get("accion", "").strip()
    modulo_filtro = request.GET.get("modulo", "").strip()


    # Búsqueda general

    if busqueda:
        registros = registros.filter(
            Q(usuario__username__icontains=busqueda) |
            Q(modulo__icontains=busqueda) |
            Q(registro__icontains=busqueda) |
            Q(descripcion__icontains=busqueda) |
            Q(direccion_ip__icontains=busqueda)
        )


    # Filtro por acción

    acciones_validas = [
        RegistroAuditoria.Accion.INICIAR_SESION,
        RegistroAuditoria.Accion.CERRAR_SESION,
        RegistroAuditoria.Accion.CREAR,
        RegistroAuditoria.Accion.EDITAR,
        RegistroAuditoria.Accion.DESACTIVAR,
    ]

    if accion_filtro in acciones_validas:
        registros = registros.filter(
            accion=accion_filtro
        )


    # Filtro por módulo

    modulos_disponibles = (
        RegistroAuditoria.objects
        .exclude(modulo="")
        .values_list("modulo", flat=True)
        .distinct()
        .order_by("modulo")
    )

    if modulo_filtro:
        registros = registros.filter(
            modulo=modulo_filtro
        )


    # ==========================
    # CONTADORES
    # ==========================

    total_registros = RegistroAuditoria.objects.count()

    total_creaciones = RegistroAuditoria.objects.filter(
        accion=RegistroAuditoria.Accion.CREAR
    ).count()

    total_ediciones = RegistroAuditoria.objects.filter(
        accion=RegistroAuditoria.Accion.EDITAR
    ).count()

    total_autenticaciones = RegistroAuditoria.objects.filter(
        accion=RegistroAuditoria.Accion.INICIAR_SESION
    ).count()


    return render(
        request,
        "auditoria/lista_auditoria.html",
        {
            "registros": registros,

            "busqueda": busqueda,
            "accion_filtro": accion_filtro,
            "modulo_filtro": modulo_filtro,

            "modulos_disponibles": modulos_disponibles,
            "acciones": RegistroAuditoria.Accion.choices,

            "total_registros": total_registros,
            "total_creaciones": total_creaciones,
            "total_ediciones": total_ediciones,
            "total_autenticaciones": total_autenticaciones,
        }
    )
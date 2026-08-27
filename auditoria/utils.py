from .models import RegistroAuditoria


def obtener_direccion_ip(request):
    """
    Obtiene la dirección IP desde la solicitud HTTP.
    """

    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if x_forwarded_for:
        direccion_ip = x_forwarded_for.split(",")[0].strip()
    else:
        direccion_ip = request.META.get("REMOTE_ADDR")

    return direccion_ip


def registrar_auditoria(
    request,
    accion,
    modulo,
    descripcion,
    registro=""
):
    """
    Registra una acción realizada dentro del sistema.
    """

    usuario = None

    if request.user.is_authenticated:
        usuario = request.user

    RegistroAuditoria.objects.create(
        usuario=usuario,
        accion=accion,
        modulo=modulo,
        registro=registro,
        descripcion=descripcion,
        direccion_ip=obtener_direccion_ip(request),
    )
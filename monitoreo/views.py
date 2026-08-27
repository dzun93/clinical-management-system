from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.db import connection
from django.shortcuts import render
from django.utils import timezone

from usuarios.decorators import solo_administrador


@solo_administrador
def estado_sistema(request):

    # ==========================
    # CONFIGURACIÓN
    # ==========================

    database_config = settings.DATABASES["default"]

    database_name = database_config.get(
        "NAME",
        "No disponible"
    )

    database_host = database_config.get(
        "HOST"
    ) or "localhost"

    database_port = database_config.get(
        "PORT"
    ) or "5432"

    backup_directory = (
        Path(settings.BASE_DIR) /
        "backups"
    )

    external_directory = Path(
        r"C:\Users\Zunig\OneDrive\Sistema_Gestion_Clinica_Backups"
    )

    log_path = (
        Path(settings.BASE_DIR) /
        "logs" /
        "respaldos.log"
    )

    # Un respaldo diario debería ser
    # renovado antes de superar este límite.
    limite_respaldo_horas = 30


    # ==========================
    # APLICACIÓN DJANGO
    # ==========================

    aplicacion_operativa = True


    # ==========================
    # POSTGRESQL
    # ==========================

    base_datos_operativa = False
    base_datos_error = ""

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                "SELECT 1"
            )

            resultado = cursor.fetchone()

            base_datos_operativa = (
                resultado is not None
                and resultado[0] == 1
            )

    except Exception as error:

        base_datos_operativa = False
        base_datos_error = str(error)


    # ==========================
    # ÚLTIMO RESPALDO LOCAL
    # ==========================

    ultimo_respaldo = None
    respaldo_local_disponible = False
    respaldo_vigente = False
    antiguedad_respaldo_horas = None

    if backup_directory.exists():

        archivos = list(
            backup_directory.glob(
                f"{database_name}_*.backup"
            )
        )

        if archivos:

            archivo_mas_reciente = max(
                archivos,
                key=lambda archivo: archivo.stat().st_mtime
            )

            estadisticas = (
                archivo_mas_reciente.stat()
            )

            fecha_respaldo = datetime.fromtimestamp(
                estadisticas.st_mtime,
                tz=timezone.get_current_timezone()
            )

            ahora = timezone.localtime()

            antiguedad = (
                ahora -
                fecha_respaldo
            )

            antiguedad_respaldo_horas = (
                antiguedad.total_seconds()
                / 3600
            )

            respaldo_vigente = (
                antiguedad_respaldo_horas
                <= limite_respaldo_horas
            )

            respaldo_local_disponible = True

            ultimo_respaldo = {
                "nombre":
                    archivo_mas_reciente.name,

                "fecha":
                    fecha_respaldo,

                "tamano_mb":
                    (
                        estadisticas.st_size
                        / 1024
                        / 1024
                    ),

                "tamano_bytes":
                    estadisticas.st_size,
            }


    # ==========================
    # COPIA EXTERNA
    # ==========================

    ubicacion_externa_disponible = (
        external_directory.exists()
    )

    copia_externa_disponible = False
    copia_externa_coincidente = False

    if (
        ultimo_respaldo
        and ubicacion_externa_disponible
    ):

        copia_externa = (
            external_directory /
            ultimo_respaldo["nombre"]
        )

        if copia_externa.exists():

            copia_externa_disponible = True

            try:

                copia_externa_coincidente = (
                    copia_externa.stat().st_size
                    ==
                    ultimo_respaldo["tamano_bytes"]
                )

            except OSError:

                copia_externa_coincidente = False


    # ==========================
    # ÚLTIMO PROCESO AUTOMÁTICO
    # ==========================

    ultimo_resultado_respaldo = (
        "No disponible"
    )

    proceso_respaldo_exitoso = False

    if log_path.exists():

        try:

            contenido = log_path.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            for linea in reversed(
                contenido.splitlines()
            ):

                if "RESULTADO:" in linea:

                    ultimo_resultado_respaldo = (
                        linea
                        .replace(
                            "RESULTADO:",
                            ""
                        )
                        .strip()
                    )

                    break

        except OSError:

            ultimo_resultado_respaldo = (
                "No disponible"
            )


    proceso_respaldo_exitoso = (
        ultimo_resultado_respaldo.upper()
        == "EXITOSO"
    )


    # ==========================
    # ALTA DISPONIBILIDAD
    # ==========================

    # Actualmente existe un único nodo
    # PostgreSQL. No se simula HA.

    nodo_primario_operativo = (
        base_datos_operativa
    )

    nodo_secundario_configurado = False

    estado_alta_disponibilidad = (
        "Pendiente de segundo nodo"
    )


    # ==========================
    # ESTADO DE RESILIENCIA
    # ==========================

    resiliencia_operativa = all([
        base_datos_operativa,
        respaldo_local_disponible,
        respaldo_vigente,
        copia_externa_disponible,
        copia_externa_coincidente,
        proceso_respaldo_exitoso,
    ])


    # ==========================
    # ESTADO GENERAL
    # ==========================

    if (
        aplicacion_operativa
        and resiliencia_operativa
    ):

        estado_general = "OPERATIVO"

    elif (
        aplicacion_operativa
        and base_datos_operativa
    ):

        estado_general = "ADVERTENCIA"

    else:

        estado_general = "CRITICO"


    # ==========================
    # CONTEXTO
    # ==========================

    return render(
        request,
        "monitoreo/estado_sistema.html",
        {
            # Estado global
            "estado_general":
                estado_general,

            "aplicacion_operativa":
                aplicacion_operativa,

            "resiliencia_operativa":
                resiliencia_operativa,


            # PostgreSQL
            "base_datos_operativa":
                base_datos_operativa,

            "base_datos_error":
                base_datos_error,

            "database_name":
                database_name,

            "database_host":
                database_host,

            "database_port":
                database_port,


            # Respaldo local
            "respaldo_local_disponible":
                respaldo_local_disponible,

            "respaldo_vigente":
                respaldo_vigente,

            "ultimo_respaldo":
                ultimo_respaldo,

            "antiguedad_respaldo_horas":
                antiguedad_respaldo_horas,

            "limite_respaldo_horas":
                limite_respaldo_horas,


            # Copia externa
            "ubicacion_externa_disponible":
                ubicacion_externa_disponible,

            "copia_externa_disponible":
                copia_externa_disponible,

            "copia_externa_coincidente":
                copia_externa_coincidente,


            # Automatización
            "ultimo_resultado_respaldo":
                ultimo_resultado_respaldo,

            "proceso_respaldo_exitoso":
                proceso_respaldo_exitoso,


            # Alta disponibilidad
            "nodo_primario_operativo":
                nodo_primario_operativo,

            "nodo_secundario_configurado":
                nodo_secundario_configurado,

            "estado_alta_disponibilidad":
                estado_alta_disponibilidad,
        }
    )
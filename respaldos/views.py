from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.shortcuts import render
from django.utils import timezone

from usuarios.decorators import solo_administrador


@solo_administrador
def panel_respaldos(request):

    # ==========================
    # RUTAS
    # ==========================

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


    # ==========================
    # FUNCIÓN AUXILIAR
    # ==========================

    def obtener_informacion_archivo(archivo):

        estadisticas = archivo.stat()

        fecha = datetime.fromtimestamp(
            estadisticas.st_mtime,
            tz=timezone.get_current_timezone()
        )

        tamano_bytes = estadisticas.st_size

        return {
            "nombre": archivo.name,
            "ruta": str(archivo),
            "fecha": fecha,
            "tamano_bytes": tamano_bytes,
            "tamano_mb": tamano_bytes / 1024 / 1024,
        }


    # ==========================
    # RESPALDOS LOCALES
    # ==========================

    respaldos_locales = []

    if backup_directory.exists():

        archivos_locales = list(
            backup_directory.glob(
                "gestion_clinica_*.backup"
            )
        )

        archivos_locales.sort(
            key=lambda archivo: archivo.stat().st_mtime,
            reverse=True
        )

        respaldos_locales = [
            obtener_informacion_archivo(archivo)
            for archivo in archivos_locales
        ]


    total_respaldos_locales = len(
        respaldos_locales
    )

    ultimo_respaldo_local = (
        respaldos_locales[0]
        if respaldos_locales
        else None
    )


    # ==========================
    # RESPALDOS EXTERNOS
    # ==========================

    respaldos_externos = []

    if external_directory.exists():

        archivos_externos = list(
            external_directory.glob(
                "gestion_clinica_*.backup"
            )
        )

        archivos_externos.sort(
            key=lambda archivo: archivo.stat().st_mtime,
            reverse=True
        )

        respaldos_externos = [
            obtener_informacion_archivo(archivo)
            for archivo in archivos_externos
        ]


    total_respaldos_externos = len(
        respaldos_externos
    )

    ultimo_respaldo_externo = (
        respaldos_externos[0]
        if respaldos_externos
        else None
    )


    # ==========================
    # VERIFICAR COPIA DEL
    # ÚLTIMO RESPALDO
    # ==========================

    copia_externa_disponible = False
    copia_externa_mismo_tamano = False

    if ultimo_respaldo_local:

        copia_correspondiente = (
            external_directory /
            ultimo_respaldo_local["nombre"]
        )

        if copia_correspondiente.exists():

            copia_externa_disponible = True

            try:

                tamano_externo = (
                    copia_correspondiente.stat().st_size
                )

                copia_externa_mismo_tamano = (
                    tamano_externo
                    ==
                    ultimo_respaldo_local["tamano_bytes"]
                )

            except OSError:

                copia_externa_mismo_tamano = False


    # ==========================
    # TAMAÑO TOTAL LOCAL
    # ==========================

    total_bytes_local = sum(
        respaldo["tamano_bytes"]
        for respaldo in respaldos_locales
    )

    total_mb_local = (
        total_bytes_local /
        1024 /
        1024
    )


    # ==========================
    # ÚLTIMO RESULTADO DEL LOG
    # ==========================

    ultimo_resultado = "No disponible"

    if log_path.exists():

        try:

            contenido_log = log_path.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            lineas = contenido_log.splitlines()

            for linea in reversed(lineas):

                if "RESULTADO:" in linea:

                    ultimo_resultado = (
                        linea
                        .replace("RESULTADO:", "")
                        .strip()
                    )

                    break

        except OSError:

            ultimo_resultado = "No disponible"


    # ==========================
    # ESTADO GENERAL
    # ==========================

    respaldo_local_disponible = (
        ultimo_respaldo_local is not None
    )

    ubicacion_externa_disponible = (
        external_directory.exists()
    )

    proceso_exitoso = (
        ultimo_resultado.upper()
        ==
        "EXITOSO"
    )


    # ==========================
    # CONTEXTO
    # ==========================

    return render(
        request,
        "respaldos/panel_respaldos.html",
        {
            # Estado general
            "respaldo_local_disponible":
                respaldo_local_disponible,

            "ubicacion_externa_disponible":
                ubicacion_externa_disponible,

            "copia_externa_disponible":
                copia_externa_disponible,

            "copia_externa_mismo_tamano":
                copia_externa_mismo_tamano,

            "proceso_exitoso":
                proceso_exitoso,

            "ultimo_resultado":
                ultimo_resultado,


            # Últimos respaldos
            "ultimo_respaldo_local":
                ultimo_respaldo_local,

            "ultimo_respaldo_externo":
                ultimo_respaldo_externo,


            # Contadores
            "total_respaldos_locales":
                total_respaldos_locales,

            "total_respaldos_externos":
                total_respaldos_externos,

            "total_mb_local":
                total_mb_local,


            # Historial
            "respaldos_locales":
                respaldos_locales[:10],

            "respaldos_externos":
                respaldos_externos[:10],


            # Configuración visible
            "dias_retencion": 30,

            "ruta_local":
                str(backup_directory),

            "ruta_externa":
                str(external_directory),
        }
    )
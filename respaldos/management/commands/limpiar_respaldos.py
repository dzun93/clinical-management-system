import time
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    help = (
        "Elimina respaldos locales antiguos según una política "
        "de retención, conservando siempre el respaldo más reciente."
    )


    def add_arguments(self, parser):

        parser.add_argument(
            "--dias",
            type=int,
            default=30,
            help=(
                "Cantidad de días que se conservarán los respaldos. "
                "Valor predeterminado: 30."
            ),
        )

        parser.add_argument(
            "--simular",
            action="store_true",
            help=(
                "Muestra qué respaldos serían eliminados "
                "sin borrar archivos."
            ),
        )


    def handle(self, *args, **options):

        dias_retencion = options["dias"]
        simular = options["simular"]


        # ==========================
        # VALIDAR RETENCIÓN
        # ==========================

        if dias_retencion < 1:
            raise CommandError(
                "El período de retención debe ser "
                "de al menos 1 día."
            )


        # ==========================
        # CONFIGURACIÓN
        # ==========================

        database_config = settings.DATABASES["default"]

        database_name = database_config.get("NAME")

        if not database_name:
            raise CommandError(
                "No se encontró el nombre de la base de datos."
            )


        backup_directory = (
            Path(settings.BASE_DIR) /
            "backups"
        )


        if not backup_directory.exists():

            self.stdout.write(
                self.style.WARNING(
                    "La carpeta de respaldos no existe."
                )
            )

            return


        # ==========================
        # LOCALIZAR RESPALDOS
        # ==========================

        patron = (
            f"{database_name}_*.backup"
        )

        respaldos = list(
            backup_directory.glob(
                patron
            )
        )


        if not respaldos:

            self.stdout.write(
                self.style.WARNING(
                    "No se encontraron respaldos "
                    "para aplicar la política de retención."
                )
            )

            return


        # Ordenar del más reciente al más antiguo.
        respaldos.sort(
            key=lambda archivo: archivo.stat().st_mtime,
            reverse=True
        )


        respaldo_mas_reciente = respaldos[0]


        # ==========================
        # CALCULAR FECHA LÍMITE
        # ==========================

        ahora = time.time()

        segundos_retencion = (
            dias_retencion *
            24 *
            60 *
            60
        )

        limite = (
            ahora -
            segundos_retencion
        )


        # ==========================
        # DETERMINAR QUÉ ELIMINAR
        # ==========================

        candidatos = []

        # Empezamos desde [1:] para excluir
        # siempre el respaldo más reciente.
        for respaldo in respaldos[1:]:

            fecha_modificacion = (
                respaldo.stat().st_mtime
            )

            if fecha_modificacion < limite:

                candidatos.append(
                    respaldo
                )


        # ==========================
        # INFORMACIÓN GENERAL
        # ==========================

        self.stdout.write(
            f"Política de retención: "
            f"{dias_retencion} días"
        )

        self.stdout.write(
            f"Respaldos encontrados: "
            f"{len(respaldos)}"
        )

        self.stdout.write(
            f"Respaldo protegido: "
            f"{respaldo_mas_reciente.name}"
        )

        self.stdout.write(
            f"Respaldos candidatos a eliminación: "
            f"{len(candidatos)}"
        )

        self.stdout.write("")


        # ==========================
        # NADA QUE ELIMINAR
        # ==========================

        if not candidatos:

            self.stdout.write(
                self.style.SUCCESS(
                    "No existen respaldos antiguos "
                    "que deban eliminarse."
                )
            )

            return


        # ==========================
        # MODO SIMULACIÓN
        # ==========================

        if simular:

            self.stdout.write(
                self.style.WARNING(
                    "MODO SIMULACIÓN: "
                    "no se eliminará ningún archivo."
                )
            )

            self.stdout.write("")

            for respaldo in candidatos:

                self.stdout.write(
                    f"Se eliminaría: "
                    f"{respaldo.name}"
                )

            self.stdout.write("")

            self.stdout.write(
                self.style.SUCCESS(
                    "Simulación completada."
                )
            )

            return


        # ==========================
        # ELIMINAR RESPALDOS
        # ==========================

        eliminados = 0
        bytes_liberados = 0
        errores = []


        for respaldo in candidatos:

            try:

                tamano = (
                    respaldo.stat().st_size
                )

                respaldo.unlink()

                eliminados += 1
                bytes_liberados += tamano

                self.stdout.write(
                    f"Eliminado: "
                    f"{respaldo.name}"
                )

            except OSError as error:

                errores.append(
                    (
                        respaldo.name,
                        str(error)
                    )
                )


        # ==========================
        # RESULTADO
        # ==========================

        espacio_mb = (
            bytes_liberados /
            1024 /
            1024
        )

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                f"Respaldos eliminados: "
                f"{eliminados}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Espacio liberado: "
                f"{espacio_mb:.2f} MB"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Respaldo más reciente conservado: "
                f"{respaldo_mas_reciente.name}"
            )
        )


        # ==========================
        # ERRORES
        # ==========================

        if errores:

            self.stdout.write("")

            for nombre, error in errores:

                self.stderr.write(
                    self.style.ERROR(
                        f"No se pudo eliminar "
                        f"{nombre}: {error}"
                    )
                )

            raise CommandError(
                "La limpieza terminó con uno "
                "o más errores."
            )
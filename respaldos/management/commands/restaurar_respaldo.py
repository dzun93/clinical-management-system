import os
import shutil
import subprocess
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    help = (
        "Restaura el respaldo PostgreSQL más reciente "
        "en una base de datos independiente de prueba."
    )

    def add_arguments(self, parser):

        parser.add_argument(
            "--reemplazar",
            action="store_true",
            help=(
                "Elimina y vuelve a crear la base de restauración "
                "si ya existe."
            ),
        )


    def localizar_programa(self, nombre):

        programa = shutil.which(nombre)

        if programa:
            return programa

        program_files = Path(
            os.environ.get(
                "ProgramFiles",
                r"C:\Program Files"
            )
        )

        postgresql_directory = (
            program_files /
            "PostgreSQL"
        )

        candidatos = []

        if postgresql_directory.exists():

            for version_directory in postgresql_directory.iterdir():

                posible_programa = (
                    version_directory /
                    "bin" /
                    f"{nombre}.exe"
                )

                if posible_programa.exists():
                    candidatos.append(
                        posible_programa
                    )

        if candidatos:

            return str(
                max(
                    candidatos,
                    key=lambda ruta: ruta.stat().st_mtime
                )
            )

        return None


    def ejecutar_comando(
        self,
        comando,
        entorno,
        descripcion_error
    ):

        try:

            return subprocess.run(
                comando,
                env=entorno,
                capture_output=True,
                text=True,
                check=True
            )

        except subprocess.CalledProcessError as error:

            mensaje = (
                error.stderr.strip()
                or error.stdout.strip()
                or descripcion_error
            )

            raise CommandError(
                f"{descripcion_error}: {mensaje}"
            )

        except OSError as error:

            raise CommandError(
                f"{descripcion_error}: {error}"
            )


    def handle(self, *args, **options):

        # ==========================
        # CONFIGURACIÓN
        # ==========================

        database_config = settings.DATABASES["default"]

        engine = database_config.get("ENGINE", "")

        if "postgresql" not in engine:
            raise CommandError(
                "Este comando está diseñado para PostgreSQL."
            )

        database_name = database_config.get("NAME")
        database_user = database_config.get("USER")
        database_password = database_config.get("PASSWORD")
        database_host = database_config.get("HOST")
        database_port = database_config.get("PORT")

        if not database_name:
            raise CommandError(
                "No se encontró el nombre de la base de datos."
            )

        if not database_user:
            raise CommandError(
                "No se encontró el usuario de PostgreSQL."
            )


        # ==========================
        # BASE DE RESTAURACIÓN
        # ==========================

        restoration_database = (
            f"{database_name}_restauracion"
        )

        # Protección crítica:
        # nunca permitir restaurar sobre la BD principal.
        if restoration_database == database_name:
            raise CommandError(
                "La base de restauración no puede ser "
                "la misma base de producción."
            )


        # ==========================
        # LOCALIZAR RESPALDO
        # ==========================

        backup_directory = (
            Path(settings.BASE_DIR) /
            "backups"
        )

        if not backup_directory.exists():
            raise CommandError(
                "No existe la carpeta de respaldos."
            )

        backups = list(
            backup_directory.glob("*.backup")
        )

        if not backups:
            raise CommandError(
                "No se encontraron archivos .backup."
            )

        backup_path = max(
            backups,
            key=lambda archivo: archivo.stat().st_mtime
        )


        # ==========================
        # PROGRAMAS POSTGRESQL
        # ==========================

        pg_restore = self.localizar_programa(
            "pg_restore"
        )

        createdb = self.localizar_programa(
            "createdb"
        )

        dropdb = self.localizar_programa(
            "dropdb"
        )

        if not pg_restore:
            raise CommandError(
                "No se encontró pg_restore."
            )

        if not createdb:
            raise CommandError(
                "No se encontró createdb."
            )

        if not dropdb:
            raise CommandError(
                "No se encontró dropdb."
            )


        # ==========================
        # ENTORNO POSTGRESQL
        # ==========================

        entorno = os.environ.copy()

        if database_password:
            entorno["PGPASSWORD"] = str(
                database_password
            )


        # ==========================
        # PARÁMETROS DE CONEXIÓN
        # ==========================

        parametros_conexion = [
            "--username",
            str(database_user),
            "--no-password",
        ]

        if database_host:

            parametros_conexion.extend(
                [
                    "--host",
                    str(database_host),
                ]
            )

        if database_port:

            parametros_conexion.extend(
                [
                    "--port",
                    str(database_port),
                ]
            )


        # ==========================
        # VALIDAR RESPALDO
        # ==========================

        self.stdout.write(
            f"Validando respaldo: {backup_path.name}"
        )

        comando_validar = [
            str(pg_restore),
            "--list",
            str(backup_path),
        ]

        self.ejecutar_comando(
            comando_validar,
            entorno,
            "El archivo de respaldo no pudo ser validado"
        )

        self.stdout.write(
            self.style.SUCCESS(
                "El archivo de respaldo es válido."
            )
        )


        # ==========================
        # REEMPLAZAR BD DE PRUEBA
        # ==========================

        if options["reemplazar"]:

            self.stdout.write(
                "Eliminando base de restauración anterior..."
            )

            comando_drop = [
                str(dropdb),
                *parametros_conexion,
                "--if-exists",
                "--force",
                restoration_database,
            ]

            self.ejecutar_comando(
                comando_drop,
                entorno,
                "No fue posible eliminar la base "
                "de restauración anterior"
            )


        # ==========================
        # CREAR BD DE RESTAURACIÓN
        # ==========================

        self.stdout.write(
            f"Creando base de datos "
            f"{restoration_database}..."
        )

        comando_create = [
            str(createdb),
            *parametros_conexion,
            "--owner",
            str(database_user),
            restoration_database,
        ]

        self.ejecutar_comando(
            comando_create,
            entorno,
            (
                "No fue posible crear la base de restauración. "
                "Si ya existe, ejecute nuevamente "
                "con --reemplazar"
            )
        )


        # ==========================
        # RESTAURAR RESPALDO
        # ==========================

        self.stdout.write(
            "Restaurando respaldo..."
        )

        comando_restore = [
            str(pg_restore),
            *parametros_conexion,
            "--dbname",
            restoration_database,
            "--exit-on-error",
            "--no-owner",
            str(backup_path),
        ]

        try:

            self.ejecutar_comando(
                comando_restore,
                entorno,
                "La restauración falló"
            )

        except CommandError:

            self.stdout.write(
                self.style.ERROR(
                    "La base de restauración fue creada, "
                    "pero el proceso de restauración falló."
                )
            )

            raise


        # ==========================
        # RESULTADO
        # ==========================

        self.stdout.write(
            self.style.SUCCESS(
                "Restauración completada correctamente."
            )
        )

        self.stdout.write(
            f"Respaldo utilizado: {backup_path}"
        )

        self.stdout.write(
            f"Base original: {database_name}"
        )

        self.stdout.write(
            f"Base restaurada: {restoration_database}"
        )

        self.stdout.write(
            self.style.WARNING(
                "La base original NO fue modificada."
            )
        )
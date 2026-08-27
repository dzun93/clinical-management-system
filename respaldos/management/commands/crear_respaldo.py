import os
import shutil
import subprocess
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone


class Command(BaseCommand):

    help = "Crea un respaldo completo de la base de datos PostgreSQL."

    def handle(self, *args, **options):

        # ==========================
        # CONFIGURACIÓN DE LA BD
        # ==========================

        database_config = settings.DATABASES["default"]

        engine = database_config.get("ENGINE", "")

        if "postgresql" not in engine:
            raise CommandError(
                "El comando de respaldo está diseñado para PostgreSQL."
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
        # LOCALIZAR pg_dump
        # ==========================

        pg_dump = shutil.which("pg_dump")

        if not pg_dump:

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

                    posible_pg_dump = (
                        version_directory /
                        "bin" /
                        "pg_dump.exe"
                    )

                    if posible_pg_dump.exists():
                        candidatos.append(
                            posible_pg_dump
                        )

            if candidatos:

                pg_dump = str(
                    max(
                        candidatos,
                        key=lambda ruta: ruta.stat().st_mtime
                    )
                )


        if not pg_dump:
            raise CommandError(
                "No se encontró pg_dump. "
                "Verifique que PostgreSQL esté instalado "
                "y que su carpeta bin esté disponible."
            )


        # ==========================
        # CARPETA DE RESPALDOS
        # ==========================

        backup_directory = (
            Path(settings.BASE_DIR) /
            "backups"
        )

        backup_directory.mkdir(
            parents=True,
            exist_ok=True
        )


        # ==========================
        # NOMBRE DEL ARCHIVO
        # ==========================

        fecha_hora = timezone.now()

        if settings.USE_TZ:
            fecha_hora = timezone.localtime(
                fecha_hora
            )

        timestamp = fecha_hora.strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        backup_filename = (
            f"{database_name}_{timestamp}.backup"
        )

        backup_path = (
            backup_directory /
            backup_filename
        )


        # ==========================
        # COMANDO pg_dump
        # ==========================

        comando = [
            str(pg_dump),
            "--format=custom",
            "--file",
            str(backup_path),
            "--username",
            str(database_user),
            "--no-password",
        ]


        if database_host:

            comando.extend(
                [
                    "--host",
                    str(database_host),
                ]
            )


        if database_port:

            comando.extend(
                [
                    "--port",
                    str(database_port),
                ]
            )


        comando.append(
            str(database_name)
        )


        # ==========================
        # VARIABLES DE ENTORNO
        # ==========================

        entorno = os.environ.copy()

        if database_password:
            entorno["PGPASSWORD"] = str(
                database_password
            )


        # ==========================
        # CREAR RESPALDO
        # ==========================

        self.stdout.write(
            "Creando respaldo de PostgreSQL..."
        )

        try:

            resultado = subprocess.run(
                comando,
                env=entorno,
                capture_output=True,
                text=True,
                check=True
            )

        except subprocess.CalledProcessError as error:

            if backup_path.exists():
                backup_path.unlink()

            mensaje_error = (
                error.stderr.strip()
                or error.stdout.strip()
                or "pg_dump finalizó con un error."
            )

            raise CommandError(
                f"No fue posible crear el respaldo: "
                f"{mensaje_error}"
            )

        except OSError as error:

            if backup_path.exists():
                backup_path.unlink()

            raise CommandError(
                f"No fue posible ejecutar pg_dump: "
                f"{error}"
            )


        # ==========================
        # VALIDAR ARCHIVO
        # ==========================

        if not backup_path.exists():

            raise CommandError(
                "pg_dump terminó sin errores, "
                "pero no se encontró el archivo de respaldo."
            )


        if backup_path.stat().st_size == 0:

            backup_path.unlink()

            raise CommandError(
                "El archivo de respaldo fue creado vacío."
            )


        # ==========================
        # RESULTADO
        # ==========================

        tamano_bytes = backup_path.stat().st_size

        tamano_mb = (
            tamano_bytes /
            1024 /
            1024
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Respaldo creado correctamente."
            )
        )

        self.stdout.write(
            f"Archivo: {backup_path}"
        )

        self.stdout.write(
            f"Tamaño: {tamano_mb:.2f} MB"
        )
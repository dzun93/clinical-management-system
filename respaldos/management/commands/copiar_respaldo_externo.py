import hashlib
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    help = (
        "Copia el respaldo PostgreSQL más reciente a la "
        "ubicación externa configurada y verifica su integridad."
    )


    # ==========================
    # CALCULAR SHA-256
    # ==========================

    def calcular_sha256(self, archivo):

        sha256 = hashlib.sha256()

        with open(archivo, "rb") as fichero:

            for bloque in iter(
                lambda: fichero.read(1024 * 1024),
                b""
            ):

                sha256.update(bloque)

        return sha256.hexdigest()


    # ==========================
    # COMANDO PRINCIPAL
    # ==========================

    def handle(self, *args, **options):

        # ==========================
        # CONFIGURACIÓN
        # ==========================

        database_config = settings.DATABASES["default"]

        database_name = database_config.get("NAME")

        if not database_name:
            raise CommandError(
                "No se encontró el nombre de la base de datos."
            )


        # ==========================
        # ORIGEN
        # ==========================

        backup_directory = (
            Path(settings.BASE_DIR) /
            "backups"
        )

        if not backup_directory.exists():

            raise CommandError(
                "La carpeta local de respaldos no existe."
            )


        patron = (
            f"{database_name}_*.backup"
        )

        respaldos = list(
            backup_directory.glob(
                patron
            )
        )


        if not respaldos:

            raise CommandError(
                "No se encontraron respaldos locales."
            )


        # Respaldo más reciente

        respaldo_origen = max(
            respaldos,
            key=lambda archivo: archivo.stat().st_mtime
        )


        # ==========================
        # DESTINO EXTERNO
        # ==========================

        destino_directory = Path(
            r"C:\Users\Zunig\OneDrive\Sistema_Gestion_Clinica_Backups"
        )

        try:

            destino_directory.mkdir(
                parents=True,
                exist_ok=True
            )

        except OSError as error:

            raise CommandError(
                f"No fue posible acceder a la carpeta externa: "
                f"{error}"
            )


        respaldo_destino = (
            destino_directory /
            respaldo_origen.name
        )


        # Archivo temporal durante la copia.
        # Evita considerar válida una copia incompleta.

        respaldo_temporal = (
            destino_directory /
            f"{respaldo_origen.name}.part"
        )


        # ==========================
        # INFORMACIÓN
        # ==========================

        self.stdout.write(
            "Copiando respaldo a ubicación externa..."
        )

        self.stdout.write(
            f"Origen: {respaldo_origen}"
        )

        self.stdout.write(
            f"Destino: {respaldo_destino}"
        )

        self.stdout.write("")


        # ==========================
        # HASH DEL ORIGINAL
        # ==========================

        self.stdout.write(
            "Calculando integridad del respaldo original..."
        )

        hash_origen = self.calcular_sha256(
            respaldo_origen
        )


        # ==========================
        # COPIAR
        # ==========================

        try:

            if respaldo_temporal.exists():
                respaldo_temporal.unlink()

            shutil.copy2(
                respaldo_origen,
                respaldo_temporal
            )

        except OSError as error:

            if respaldo_temporal.exists():

                try:
                    respaldo_temporal.unlink()
                except OSError:
                    pass

            raise CommandError(
                f"No fue posible copiar el respaldo: {error}"
            )


        # ==========================
        # VERIFICAR TAMAÑO
        # ==========================

        tamano_origen = (
            respaldo_origen.stat().st_size
        )

        tamano_destino = (
            respaldo_temporal.stat().st_size
        )


        if tamano_origen != tamano_destino:

            respaldo_temporal.unlink()

            raise CommandError(
                "La copia externa tiene un tamaño diferente "
                "al archivo original."
            )


        # ==========================
        # VERIFICAR SHA-256
        # ==========================

        self.stdout.write(
            "Verificando integridad de la copia..."
        )

        hash_destino = self.calcular_sha256(
            respaldo_temporal
        )


        if hash_origen != hash_destino:

            respaldo_temporal.unlink()

            raise CommandError(
                "La verificación SHA-256 falló. "
                "La copia externa no coincide con el respaldo original."
            )


        # ==========================
        # FINALIZAR COPIA
        # ==========================

        try:

            respaldo_temporal.replace(
                respaldo_destino
            )

        except OSError as error:

            raise CommandError(
                f"No fue posible finalizar la copia externa: "
                f"{error}"
            )


        # ==========================
        # RESULTADO
        # ==========================

        tamano_mb = (
            respaldo_destino.stat().st_size
            / 1024
            / 1024
        )


        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "Copia externa creada correctamente."
            )
        )

        self.stdout.write(
            f"Archivo: {respaldo_destino}"
        )

        self.stdout.write(
            f"Tamaño: {tamano_mb:.2f} MB"
        )

        self.stdout.write(
            f"SHA-256: {hash_destino}"
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Integridad de la copia verificada."
            )
        )
from django.core.management import (
    BaseCommand,
    CommandError,
    call_command,
)


class Command(BaseCommand):

    help = (
        "Ejecuta el proceso automático de respaldo: "
        "creación, copia externa y política de retención."
    )


    def add_arguments(self, parser):

        parser.add_argument(
            "--dias",
            type=int,
            default=30,
            help=(
                "Cantidad de días que se conservarán "
                "los respaldos. Valor predeterminado: 30."
            ),
        )


    def handle(self, *args, **options):

        dias_retencion = options["dias"]

        if dias_retencion < 1:
            raise CommandError(
                "El período de retención debe ser "
                "de al menos 1 día."
            )


        # ==========================
        # INICIO
        # ==========================

        self.stdout.write(
            "=========================================="
        )

        self.stdout.write(
            "PROCESO AUTOMÁTICO DE RESPALDO"
        )

        self.stdout.write(
            "=========================================="
        )

        self.stdout.write("")


        # ==========================
        # PASO 1: CREAR RESPALDO
        # ==========================

        self.stdout.write(
            "Paso 1 de 3: creando respaldo..."
        )

        self.stdout.write("")

        try:

            call_command(
                "crear_respaldo",
                stdout=self.stdout,
                stderr=self.stderr,
            )

        except CommandError as error:

            raise CommandError(
                f"El proceso automático se detuvo porque "
                f"no fue posible crear el respaldo: {error}"
            )


        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "Paso 1 completado."
            )
        )

        self.stdout.write("")


        # ==========================
        # PASO 2: COPIA EXTERNA
        # ==========================

        self.stdout.write(
            "Paso 2 de 3: copiando respaldo "
            "a ubicación externa..."
        )

        self.stdout.write("")

        try:

            call_command(
                "copiar_respaldo_externo",
                stdout=self.stdout,
                stderr=self.stderr,
            )

        except CommandError as error:

            raise CommandError(
                f"El respaldo local fue creado, "
                f"pero la copia externa falló: {error}"
            )


        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "Paso 2 completado."
            )
        )

        self.stdout.write("")


        # ==========================
        # PASO 3: RETENCIÓN
        # ==========================

        self.stdout.write(
            f"Paso 3 de 3: aplicando política "
            f"de retención de {dias_retencion} días..."
        )

        self.stdout.write("")

        try:

            call_command(
                "limpiar_respaldos",
                dias=dias_retencion,
                stdout=self.stdout,
                stderr=self.stderr,
            )

        except CommandError as error:

            self.stdout.write("")

            self.stdout.write(
                self.style.WARNING(
                    "El respaldo local y la copia externa "
                    "fueron creados correctamente, pero ocurrió "
                    "un problema durante la limpieza."
                )
            )

            raise CommandError(
                f"Error durante la política de retención: "
                f"{error}"
            )


        # ==========================
        # RESULTADO FINAL
        # ==========================

        self.stdout.write("")

        self.stdout.write(
            "=========================================="
        )

        self.stdout.write(
            self.style.SUCCESS(
                "PROCESO AUTOMÁTICO COMPLETADO"
            )
        )

        self.stdout.write(
            "=========================================="
        )

        self.stdout.write(
            self.style.SUCCESS(
                "El respaldo local fue creado, "
                "la copia externa fue verificada "
                "y la política de retención fue aplicada."
            )
        )
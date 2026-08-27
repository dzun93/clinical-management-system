import psycopg
from psycopg import sql

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    help = (
        "Compara las tablas críticas de la base principal "
        "con la base de datos restaurada."
    )


    # ==========================
    # CONEXIÓN
    # ==========================

    def obtener_parametros_conexion(
        self,
        database_config,
        database_name
    ):

        parametros = {
            "dbname": database_name,
            "user": database_config.get("USER"),
        }

        password = database_config.get("PASSWORD")
        host = database_config.get("HOST")
        port = database_config.get("PORT")

        if password:
            parametros["password"] = password

        if host:
            parametros["host"] = host

        if port:
            parametros["port"] = port

        return parametros


    # ==========================
    # VERIFICAR TABLA
    # ==========================

    def obtener_total_registros(
        self,
        conexion,
        tabla
    ):

        consulta_existencia = """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = %s
            )
        """

        resultado = conexion.execute(
            consulta_existencia,
            (tabla,)
        ).fetchone()

        existe = resultado[0]

        if not existe:
            return None

        consulta_conteo = sql.SQL(
            "SELECT COUNT(*) FROM {}"
        ).format(
            sql.Identifier(tabla)
        )

        resultado = conexion.execute(
            consulta_conteo
        ).fetchone()

        return resultado[0]


    # ==========================
    # COMANDO PRINCIPAL
    # ==========================

    def handle(self, *args, **options):

        database_config = settings.DATABASES["default"]

        engine = database_config.get(
            "ENGINE",
            ""
        )

        if "postgresql" not in engine:
            raise CommandError(
                "Este comando está diseñado para PostgreSQL."
            )


        # ==========================
        # NOMBRES DE BASES
        # ==========================

        database_original = database_config.get(
            "NAME"
        )

        if not database_original:
            raise CommandError(
                "No se encontró el nombre de la base "
                "de datos principal."
            )

        database_restaurada = (
            f"{database_original}_restauracion"
        )


        # ==========================
        # TABLAS CRÍTICAS
        # ==========================

        tablas = {
            "Pacientes":
                "pacientes_paciente",

            "Expedientes clínicos":
                "expedientes_expedienteclinico",

            "Consultas médicas":
                "consultas_consultamedica",

            "Citas":
                "citas_cita",

            "Usuarios":
                "auth_user",

            "Perfiles de usuario":
                "usuarios_perfilusuario",

            "Registros de auditoría":
                "auditoria_registroauditoria",
        }


        # ==========================
        # PARÁMETROS
        # ==========================

        parametros_original = (
            self.obtener_parametros_conexion(
                database_config,
                database_original
            )
        )

        parametros_restaurada = (
            self.obtener_parametros_conexion(
                database_config,
                database_restaurada
            )
        )


        # ==========================
        # CONECTAR
        # ==========================

        self.stdout.write(
            "Verificando restauración..."
        )

        self.stdout.write(
            f"Base original: {database_original}"
        )

        self.stdout.write(
            f"Base restaurada: {database_restaurada}"
        )

        self.stdout.write("")


        try:

            conexion_original = psycopg.connect(
                **parametros_original
            )

        except Exception as error:

            raise CommandError(
                f"No fue posible conectar con la "
                f"base original: {error}"
            )


        try:

            conexion_restaurada = psycopg.connect(
                **parametros_restaurada
            )

        except Exception as error:

            conexion_original.close()

            raise CommandError(
                f"No fue posible conectar con la "
                f"base restaurada: {error}"
            )


        # ==========================
        # COMPARAR DATOS
        # ==========================

        diferencias = False
        tablas_faltantes = False

        try:

            self.stdout.write(
                "------------------------------------------------------------"
            )

            self.stdout.write(
                f"{'Módulo':<25}"
                f"{'Original':>12}"
                f"{'Restaurada':>15}"
                f"{'Estado':>8}"
            )

            self.stdout.write(
                "------------------------------------------------------------"
            )


            for nombre, tabla in tablas.items():

                total_original = (
                    self.obtener_total_registros(
                        conexion_original,
                        tabla
                    )
                )

                total_restaurada = (
                    self.obtener_total_registros(
                        conexion_restaurada,
                        tabla
                    )
                )


                # ==========================
                # TABLA FALTANTE
                # ==========================

                if total_original is None:
                    original_texto = "NO EXISTE"
                    tablas_faltantes = True
                else:
                    original_texto = str(
                        total_original
                    )


                if total_restaurada is None:
                    restaurada_texto = "NO EXISTE"
                    tablas_faltantes = True
                else:
                    restaurada_texto = str(
                        total_restaurada
                    )


                # ==========================
                # COMPARACIÓN
                # ==========================

                if (
                    total_original is not None
                    and total_restaurada is not None
                    and total_original == total_restaurada
                ):

                    estado = "OK"

                else:

                    estado = "DIF."

                    diferencias = True


                self.stdout.write(
                    f"{nombre:<25}"
                    f"{original_texto:>12}"
                    f"{restaurada_texto:>15}"
                    f"{estado:>8}"
                )


            self.stdout.write(
                "------------------------------------------------------------"
            )


        finally:

            conexion_original.close()
            conexion_restaurada.close()


        # ==========================
        # RESULTADO FINAL
        # ==========================

        self.stdout.write("")


        if tablas_faltantes:

            raise CommandError(
                "La verificación detectó una o más "
                "tablas críticas ausentes."
            )


        if diferencias:

            self.stdout.write(
                self.style.WARNING(
                    "Se encontraron diferencias entre "
                    "la base actual y la base restaurada."
                )
            )

            self.stdout.write(
                self.style.WARNING(
                    "Esto puede significar que la base principal "
                    "cambió después de crear el respaldo."
                )
            )

            self.stdout.write(
                self.style.WARNING(
                    "Revise las diferencias antes de considerar "
                    "las bases equivalentes."
                )
            )

            return


        self.stdout.write(
            self.style.SUCCESS(
                "VERIFICACIÓN COMPLETADA CORRECTAMENTE."
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Las tablas críticas existen y sus cantidades "
                "de registros coinciden."
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "La restauración ha sido verificada."
            )
        )
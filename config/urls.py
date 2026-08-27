from django.contrib import admin
from django.urls import path, include


from django.views.generic import RedirectView

urlpatterns = [
   path(
    "",
    RedirectView.as_view(
        pattern_name="dashboard",
        permanent=False
    ),
),

    path("admin/", admin.site.urls),
    path("pacientes/", include("pacientes.urls")),
    path("expedientes/", include("expedientes.urls")),
    path("consultas/", include("consultas.urls")),
    path("citas/", include("citas.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("usuarios/", include("usuarios.urls")),

    path("reportes/", include("reportes.urls")),
    path("auditoria/", include("auditoria.urls")),
    path("respaldos/", include("respaldos.urls")),
    path("monitoreo/", include("monitoreo.urls")),

]
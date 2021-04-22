from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from rest_framework.permissions import AllowAny


schema_view = get_schema_view(
    openapi.Info(title="Butter Activities API", default_version="v1"),
    public=True,
    permission_classes=(AllowAny,),
)

urlpatterns = (
    [
        path("admin/", admin.site.urls),
        path("v1/", include("core.v1_urls")),
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)

if settings.DEBUG:
    urlpatterns.append(
        path("docs/", schema_view.with_ui("swagger", cache_timeout=0), name="swagger")
    )

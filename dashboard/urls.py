# -*- encoding: utf-8 -*-

from django.contrib import admin
from django.urls import path, include  # add this
from rest_framework import routers
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from drf_yasg.generators import OpenAPISchemaGenerator


class SchemaGenerator(OpenAPISchemaGenerator):

    def determine_path_prefix(self, paths):
        return ''


api_info = openapi.Info(
    title="Dashboard API",
    default_version='v1',
)

schema_view = get_schema_view(
    api_info,
    public=True,
    generator_class=SchemaGenerator,
)

from data import views

admin.site.site_header = "Repustate Admin"
admin.site.site_title = "Repustate Admin"
admin.site.index_title = "Welcome to Repustate"

router = routers.DefaultRouter()
router.register('data', views.DataViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),  # Django admin route
    # path('api/', include(router.urls)),
    path("", include("authentication.urls")),  # Auth routes - login / register

    #path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc-ui'),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
    path("api/", include("data.api")),  # API Urls
    path("", include("data.urls"))  # UI Kits Html files

]

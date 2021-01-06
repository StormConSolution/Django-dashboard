# -*- encoding: utf-8 -*-

from django.contrib import admin
from django.urls import path, include  # add this
from rest_framework import routers
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

api_info = openapi.Info(
    title="Dashboard API",
    default_version='v1',
)

schema_view = get_schema_view(
    api_info,
    public=True,
    permission_classes=[permissions.AllowAny],
)

from data import views

admin.site.site_header = "Repustate Admin"
admin.site.site_title = "Repustate Admin"
admin.site.index_title = "Welcome to Repustate"

router = routers.DefaultRouter()
router.register('data', views.DataViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),          # Django admin route
    # path('api/', include(router.urls)),
    path("", include("authentication.urls")),  # Auth routes - login / register

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path("", include("data.urls"))             # UI Kits Html files

]

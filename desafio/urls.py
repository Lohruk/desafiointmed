from api.views import (
    AgendaViewSet,
    ConsultaViewSet,
    DeletarConsultaViewSet,
    EspecialidadeViewSet,
    MedicoViewSet,
)
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

router = routers.DefaultRouter()
router.register(r'especialidades', EspecialidadeViewSet)
router.register(r'medicos', MedicoViewSet)
router.register(r'agendas', AgendaViewSet, basename='Agenda')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('consultas/', ConsultaViewSet.as_view(), name='consulta'),
    path('consultas/<int:pk>/', DeletarConsultaViewSet.as_view(), name='consulta'),
    path('api-token-auth/', obtain_auth_token)
]

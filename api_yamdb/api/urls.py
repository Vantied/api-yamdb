from django.urls import path, include
from rest_framework import routers


from api.views import TitleViewSet
from api.constants import VERSION

app_name = 'api'

# Создаём роутер и регистрируем ViewSet
router_v1 = routers.DefaultRouter()
router_v1.register(r'titles', TitleViewSet, basename='titles')

urlpatterns = [
    path(f'{VERSION}/', include(router_v1.urls)),
]

from django.urls import include, path
from rest_framework import routers

from api.views import CategoryViewSet, TitleViewSet
from api.constants import VERSION

app_name = 'api'

# Создаём роутер и регистрируем ViewSet
router_v1 = routers.DefaultRouter()
router_v1.register(r'titles', TitleViewSet, basename='titles')
router_v1.register(r'categories', CategoryViewSet, basename='categories')

urlpatterns = [
    path(f'{VERSION}/', include(router_v1.urls)),
]

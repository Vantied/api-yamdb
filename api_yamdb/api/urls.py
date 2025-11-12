from django.urls import include, path
from rest_framework import routers

from api.views import get_token, signup, TitleViewSet
from api.constants import VERSION

app_name = 'api'

# Создаём роутер и регистрируем ViewSet
router_v1 = routers.DefaultRouter()
router_v1.register(r'titles', TitleViewSet, basename='titles')

urlpatterns = [
    path(f'{VERSION}/', include(router_v1.urls)),
    path('auth/signup/', signup, name='signup'),
    path('auth/token/', get_token, name='token'),
]

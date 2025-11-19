from django.urls import include, path
from rest_framework import routers

from api.constants import VERSION
from api.views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    get_token,
    ReviewViewSet,
    signup,
    TitleViewSet,
    UserViewSet,
)

app_name = 'api'

# Создаём роутер и регистрируем ViewSet
router_v1 = routers.DefaultRouter()
router_v1.register(r'titles', TitleViewSet, basename='titles')
router_v1.register(r'users', UserViewSet, basename='users')
router_v1.register(r'categories', CategoryViewSet, basename='categories')
router_v1.register(r'genres', GenreViewSet, basename='genres')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)


urlpatterns = [
    path(f'{VERSION}/', include(router_v1.urls)),
    path(f'{VERSION}/auth/signup/', signup, name='signup'),
    path(f'{VERSION}/auth/token/', get_token, name='token'),
]

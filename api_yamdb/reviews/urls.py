from django.urls import include, path

from rest_framework_nested import routers

from reviews.views import CommentViewSet, ReviewViewSet

app_name = 'reviews'

router = routers.SimpleRouter()

reviews_router = routers.NestedSimpleRouter(router, r'titles', lookup='title')
reviews_router.register(r'reviews', ReviewViewSet, basename='title-reviews')

comments_router = routers.NestedSimpleRouter(reviews_router, r'reviews',
                                             lookup='review')
comments_router.register(r'comments', CommentViewSet,
                         basename='review-comments')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(reviews_router.urls)),
    path('', include(comments_router.urls)),
]

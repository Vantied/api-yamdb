from django.contrib import admin

from reviews.models import Comment, Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Админ-класс для управления отзывами в административной панели.
    """

    list_display = ('id', 'title', 'author', 'score', 'pub_date')
    list_filter = ('pub_date', 'score')
    search_fields = ('text', 'author__username', 'title__name')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Админ-класс для управления комментариями в административной панели.
    """

    list_display = ('id', 'review', 'author', 'pub_date')
    list_filter = ('pub_date',)
    search_fields = ('text', 'author__username', 'review__text')
from reviews.models import Category, Genre, Title

# Регистрация в админке
admin.site.register(Category)
admin.site.register(Genre)
admin.site.register(Title)

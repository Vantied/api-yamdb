from django.contrib import admin

from reviews.models import Category, Genre, Title

# Регистрация в админке
admin.site.register(Category)
admin.site.register(Genre)
admin.site.register(Title)
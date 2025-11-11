from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Класс разрешений, предоставляющий доступ только администраторам.

    Администраторы включают:
    - Пользователей с ролью 'admin'
    - Суперпользователей Django

    Используется для эндпоинтов, требующих полного административного доступа.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Класс разрешений, позволяющий безопасные методы (GET, HEAD, OPTIONS)
    всем пользователям, но ограничивающий операции записи
    (POST, PUT, PATCH, DELETE) только администраторам.

    Используется для эндпоинтов, где любой может читать данные,
    но только администраторы могут их изменять.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated and request.user.is_admin
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Класс разрешений, позволяющий безопасные методы всем пользователям,
    но ограничивающий операции записи только владельцу объекта.

    Используется для эндпоинтов, где пользователи могут редактировать только
    свои собственные объекты (например, свои отзывы, комментарии).
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )


class IsModeratorOrAdminOrReadOnly(permissions.BasePermission):
    """
    Класс разрешений, позволяющий безопасные методы всем пользователям,
    но ограничивающий операции записи модераторам, администраторам
    и владельцам объектов.

    Используется для эндпоинтов, где:
    - Все могут читать данные
    - Модераторы и администраторы могут редактировать любые объекты
    - Владельцы могут редактировать только свои объекты
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated and (
                request.user.is_moderator or obj.author == request.user
            )
        )

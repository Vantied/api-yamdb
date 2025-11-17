from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Разрешение для администраторов."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsAdminOrReadOnly(permissions.BasePermission):
    """Разрешение: чтение для всех, запись только для администраторов."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated and request.user.is_admin
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Разрешение: чтение для всех, запись только для владельца."""

    def has_object_permission(self, request, view, obj):
        # Разрешаем безопасные методы (GET, HEAD, OPTIONS) для всех
        if request.method in permissions.SAFE_METHODS:
            return True

        # Для методов записи проверяем, что пользователь - автор объекта
        return obj.author == request.user


class IsModeratorOrAdminOrReadOnly(permissions.BasePermission):
    """Чтение для всех, запись для модераторов, админов и владельцев."""

    def has_object_permission(self, request, view, obj):
        # Разрешаем безопасные методы (GET, HEAD, OPTIONS) для всех
        if request.method in permissions.SAFE_METHODS:
            return True

        # Для методов записи проверяем права
        return (
            request.user.is_authenticated and (
                request.user.is_moderator or request.user.is_admin
                or obj.author == request.user
            )
        )

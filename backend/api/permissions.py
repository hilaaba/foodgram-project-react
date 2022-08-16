from rest_framework.permissions import SAFE_METHODS, BasePermission


class AdminPermission(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_admin
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and request.user.is_admin
        )


class CurrentUserPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class ReadOnlyPermission(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS

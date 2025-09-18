from rest_framework import permissions


class IsAdminOrIsAuthenticatedReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff is True or (
            request.user.is_authenticated and request.method in permissions.SAFE_METHODS
        )


class IsAdminAllowDeleteOrIsAuthenticatedReadAndCreateOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff is True or (
            request.user.is_authenticated
            and request.method
            in [
                "POST",
                *permissions.SAFE_METHODS,
            ]
        )

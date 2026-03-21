from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Permission check for admin role
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin


class IsOperator(permissions.BasePermission):
    """
    Permission check for operator role
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_operator or request.user.is_admin
        )


class IsCook(permissions.BasePermission):
    """
    Permission check for cook role
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_cook or request.user.is_admin
        )

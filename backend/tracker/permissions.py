from rest_framework import permissions


class IsAdministratrice(permissions.BasePermission):
    """Permission : accès réservé à l'administratrice."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'role', None) == 'administratrice'
        )


class IsEmploye(permissions.BasePermission):
    """Permission : accès réservé aux employés authentifiés."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'role', None) == 'employe'
        )


class IsEmployeOwnSite(permissions.BasePermission):
    """
    Permission : l'employé n'accède qu'à son propre site.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'role', None) == 'employe'
        )

    def has_object_permission(self, request, view, obj):
        """Employé n'accède qu'aux objets de son site."""
        if getattr(request.user, 'role', None) != 'employe':
            return False
        if hasattr(obj, 'site'):
            return obj.site_id == request.user.site_id
        if hasattr(obj, 'site_id'):
            return obj.site_id == request.user.site_id
        return False


class IsAdministratriceOrReadOnly(permissions.BasePermission):
    """Permission : les employés peuvent lire, seule l'admin peut écrire."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'role', None) == 'administratrice'
        )
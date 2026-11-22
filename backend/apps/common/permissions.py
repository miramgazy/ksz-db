from rest_framework import permissions

class IsSuperAdmin(permissions.BasePermission):
    """
    Allows access only to users with the SUPERADMIN role.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_active and
            request.user.role == 'SUPERADMIN'
        )

class IsManagerOrSuperAdmin(permissions.BasePermission):
    """
    Allows access to users with MANAGER or SUPERADMIN role.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_active and
            request.user.role in ['SUPERADMIN', 'MANAGER']
        )

class ReadOnlyForViewer(permissions.BasePermission):
    """
    Custom permission:
    - VIEWER role has read-only access (SAFE_METHODS: GET, HEAD, OPTIONS).
    - MANAGER and SUPERADMIN have full read/write access.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated and request.user.is_active):
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        # Modification methods require MANAGER or SUPERADMIN
        return request.user.role in ['SUPERADMIN', 'MANAGER']

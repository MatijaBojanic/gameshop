from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Admin should be able to do unsafe methods on objs, while regular users should be able to do safe stuff
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return False



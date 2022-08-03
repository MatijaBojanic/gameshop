from rest_framework import permissions
from shop_api.models import Order


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Admin should be able to do unsafe methods on objs, while regular users should be able to do safe stuff
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return False


class IsSuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsCommentOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, comment):
        return request.method in permissions.SAFE_METHODS or comment.user.id == request.user.id or request.user.is_staff


class AdminOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, order):
        return order.user.id == request.user.id or request.user.is_staff


class AdminOrNotCheckedOut(permissions.BasePermission):
    def has_object_permission(self, request, view, order):
        return (order.user.id == request.user.id
                and (
                    (request.method not in permissions.SAFE_METHODS
                     and order.checkout_date == None)
                    or request.method in permissions.SAFE_METHODS)) \
               or request.user.is_staff


class AdminOrNotCheckedOutOrder(permissions.BasePermission):
    def has_permission(self, request, view):
        order_pk = request.parser_context['kwargs']['order_pk']
        order = Order.objects.get(id=order_pk)
        user_is_owner = order.user.id == request.user.id
        is_safe_method = request.method in permissions.SAFE_METHODS
        order_not_checked_out = order.checkout_date is None
        return request.user.is_staff or \
               (user_is_owner and (is_safe_method or (not is_safe_method and order_not_checked_out)))

    def has_object_permission(self, request, view, order_item):
        user_is_owner = order_item.order.user.id == request.user.id
        is_safe_method = request.method in permissions.SAFE_METHODS
        order_not_checked_out = order_item.order.checkout_date is None
        return request.user.is_staff or \
               (user_is_owner and (is_safe_method or (not is_safe_method and order_not_checked_out)))


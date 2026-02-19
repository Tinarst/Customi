from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request


class HasStoreOrSeller(BasePermission):

    def has_permission(self, request, view):
        if request.method != "POST":
            return hasattr(request.user, "store_user")

        if request.user and request.user.is_authenticated:
            return bool(request.user.role == request.user.UserRole.SELLER)

        return False


class ReadOnlyOrSeller(BasePermission):

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS
            or request.user
            and hasattr(request.user, "store_user")
        )

    def has_object_permission(self, request, view, obj):
        if request.method not in SAFE_METHODS:
            if hasattr(obj, "created_by"):
                return True if request.user == obj.created_by else False
            return True if request.user == obj.store.seller else False
        return True

class OrderItemSeller(ReadOnlyOrSeller):
    def has_object_permission(self, request, view, obj):
        return True if request.user == obj.product_store.store.seller else False

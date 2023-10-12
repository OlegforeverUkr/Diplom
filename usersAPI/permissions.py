from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework import permissions
from administrators.models import Hall, Ticket

def get_session_permissions(self):
    if self.action in ['update', 'destroy']:
        permission_classes = [IsAdminUser]
    else:
        permission_classes = [AllowAny]

    return [permission() for permission in permission_classes]



class IsAdminUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user and request.user.is_staff
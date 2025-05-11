from functools import wraps
from rest_framework.response import Response
from rest_framework import status


def custom_permission_required(permission_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(self, request, *args, **kwargs):
            if not request.user.has_custom_permission(permission_name):
                return Response(
                    {"error": "No tienes permiso para realizar esta acción"},
                    status=status.HTTP_403_FORBIDDEN
                )
            return view_func(self, request, *args, **kwargs)
        return _wrapped_view
    return decorator

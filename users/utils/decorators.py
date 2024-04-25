from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from users.models import CustomUser

from functools import wraps
from rest_framework.response import Response
from rest_framework import status

def manager_required(func):
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        user = request.user
        if user.role != CustomUser.MANAGER:
            return Response({'error': 'You do not have permission to access this resource'}, status=status.HTTP_403_FORBIDDEN)
        return func(self, request, *args, **kwargs)
    return wrapper


def employee_required(func):
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):  
        user = request.user
        if user.role != CustomUser.EMPLOYEE:
            return Response({'error': 'You do not have permission to access'}, status=status.HTTP_403_FORBIDDEN)
        return func(self, request, *args, **kwargs)  
    return wrapper

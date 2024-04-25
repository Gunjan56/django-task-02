from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import authenticate
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser
from .serializers import UserSerializer, ManagerSerializer
from users.utils.decorators import  manager_and_employee_required, manager_required
class UserRegistrationAPIView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CreateManagerAPIView(APIView):
    def post(self, request):
        serializer = ManagerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserLoginAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)
        if user:
            access_token = AccessToken.for_user(user)
            return Response({'access_token': str(access_token)})
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class UserListCreateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserRetrieveUpdateDestroyAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(CustomUser, pk=pk)

    @manager_required  
    def get(self, request, pk):
        user = self.get_object(pk)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
 

    @manager_and_employee_required
    def put(self, request, pk):
        user = self.get_object(pk)
        if user != request.user:
            return Response({'error': 'You do not have permission to update this user'}, status=status.HTTP_403_FORBIDDEN)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            if 'role' in request.data:
                return Response({'error': 'You do not have permission to update the role field'}, status=status.HTTP_403_FORBIDDEN)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @manager_required  
    def delete(self, request, pk):
        user = self.get_object(pk)
        user.delete()
        return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

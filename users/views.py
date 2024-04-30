from datetime import timedelta
from django.utils import timezone
import os
import secrets
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import authenticate
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.hashers import make_password, check_password
from .models import CustomUser, TokenLink
from .serializers import UserSerializer, ChangePasswordSerializer
from users.utils.decorators import manager_required, employee_required, manager_and_employee_required

class UserRegistrationAPIView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
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

class ChangePasswordView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            if not check_password(serializer.data.get('old_password'),user.password):
                return Response({'error': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
            if serializer.data.get('new_password') != serializer.data.get('confirm_new_password'):
                return Response({'error': 'new_password and confirm_new_password'}, status=status.HTTP_400_BAD_REQUEST)
            user.password = make_password(serializer.data.get('new_password'))
            user.save()
            return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Forgetpassword(APIView):
    def post(self, request):
        email = request.data.get("email")
        user = CustomUser.objects.get(email=email)
        try:
            user1 = TokenLink.objects.get(user_id=user.id)
        except TokenLink.DoesNotExist:
                TokenLink.objects.create(user_id=user.id)
        expires = timezone.now() + timedelta(minutes=15)
        token = secrets.token_urlsafe(4)
        encoded_email_id = urlsafe_base64_encode(email.encode())
        Reset_link = (encoded_email_id) + '.' + (token)
        url = f'http://127.0.0.1:8000/users/reset_password/'
        subject = 'Reset Your Password'
        message = "Hello," + user.username + \
            " To reset your password. Your link is : " + url + Reset_link
        email_from = os.getenv('EMAIL_HOST_USER')
        recipient_list = [user.email, ]
        send_mail(subject,message,email_from, recipient_list)
        user1.isUsed=1
        user1.token=token
        user1.expired_time=expires
        user1.save()
        return Response('email send successfully', status=status.HTTP_200_OK)

class Resetpassword(APIView):
    def post(self, request, Reset_link):
        new_password = request.data.get('new_password')
        confirm_new_password = request.data.get('confirm_new_password')
        email, token = Reset_link.split('.')
        email = urlsafe_base64_decode(email).decode()
        user = CustomUser.objects.get(email=email)
        user1 = TokenLink.objects.get(user_id=user.id)
        if user1.isUsed == 0:
            return Response({'error':'used token'}, status=status.HTTP_400_BAD_REQUEST)
        if not new_password and confirm_new_password:
            return Response({'error':'new_password and confirm_new_password missing'}, status=status.HTTP_400_BAD_REQUEST)
        if timezone.now() > user1.expired_time:
            print(timezone.now())
            return Response({'error':'The token has exxpired'}, status=status.HTTP_400_BAD_REQUEST)
        if token != user1.token:
            return Response({'error':'Wrong token provided'})
        if new_password != confirm_new_password:
            return Response({'error':'new_password and confirm_new_password do not match.'}, status=status.HTTP_400_BAD_REQUEST)
        if token == user1.token and timezone.now() < user1.expired_time:
            print(timezone.now())
            user.password = make_password(new_password)
            user.save()
            user1.isUsed = 0
            user1.save()
            return Response('Password changed successfully.', status=status.HTTP_200_OK)


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
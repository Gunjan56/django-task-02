from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.UserRegistrationAPIView.as_view()),
    path('login/', views.UserLoginAPIView.as_view()),
    path('', views.UserListCreateAPIView.as_view()),
    path('<int:pk>/', views.UserRetrieveUpdateDestroyAPIView.as_view())
]

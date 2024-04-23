from django.urls import path
from . import views

urlpatterns = [
    path('', views.TaskListCreateAPIView.as_view()),
    path('<int:pk>/', views.TaskRetrieveUpdateDestroyAPIView.as_view()),
]

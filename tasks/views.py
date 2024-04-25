from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Task
from .serializers import TaskSerializer

class TaskListCreateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(assignee=request.user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(assignor=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskRetrieveUpdateDestroyAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Task, pk=pk)

    def get(self, request, pk):
        task = self.get_object(pk)
        if task.assignee == request.user:
            serializer = TaskSerializer(task)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'You do not have permission to access this task'}, status=status.HTTP_403_FORBIDDEN)

    def put(self, request, pk):
        task = self.get_object(pk)
        if task.assignor == request.user:
            serializer = TaskSerializer(task, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'You do not have permission to update this task'}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, pk):
        task = self.get_object(pk)
        if task.assignor == request.user:
            task.delete()
            return Response({"message": "task deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': 'You do not have permission to delete this task'}, status=status.HTTP_403_FORBIDDEN)

class TaskUpdateStatusAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        if task.assignee == request.user:
            task.status = request.data.get('status')
            task.save()
            return Response({'message': 'Task status updated successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'You do not have permission to update the status of this task'}, status=status.HTTP_403_FORBIDDEN)

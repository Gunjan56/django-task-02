from rest_framework import serializers
from .models import Task
from users.models import CustomUser


class TaskSerializer(serializers.ModelSerializer):
    assignee = serializers.CharField()

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'due_date', 'status', 'assignee']

    def create(self, validated_data):
        assignee = validated_data.pop('assignee', None)
        if assignee:
            user, _ = CustomUser.objects.get_or_create(username=assignee)
            validated_data['assignee'] = user
        return Task.objects.create(**validated_data)


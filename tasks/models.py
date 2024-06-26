from django.db import models
from users.models import CustomUser

class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=(('not_started', 'Not Started'), ('in_progress', 'In Progress'), ('completed', 'Completed')), default='not_started')
    assignee = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    assignor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assigned_tasks', null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)

    
    def __str__(self):
        return self.title
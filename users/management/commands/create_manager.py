from django.core.management.base import BaseCommand
from users.models import CustomUser

class Command(BaseCommand):
    help = 'Create a manager user'

    def handle(self, *args, **kwargs):
        manager_email = input("Enter manager's email address: ")
        manager_username = input("Enter manager's username: ")
        manager_password = input("Enter manager's password: ")
        
        CustomUser.objects.create_user(email=manager_email, username=manager_username, password=manager_password, role=CustomUser.MANAGER)
        
        self.stdout.write(self.style.SUCCESS('Manager user created successfully!'))

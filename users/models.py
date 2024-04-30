from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager

class CustomUser(AbstractUser):
    EMPLOYEE = 'employee'
    MANAGER = 'manager'

    ROLE_CHOICES = [
        (EMPLOYEE, 'Employee'),
        (MANAGER, 'Manager'),
    ]

    email = models.EmailField(_("email address"), unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class TokenLink(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='link_user')
    isUsed = models.BooleanField(default=False)
    token = models.CharField(max_length=5000, null=True)
    expired_time = models.DateTimeField(null=True)
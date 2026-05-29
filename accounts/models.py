from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('operator', 'Operator'),
        ('cook', 'Cook'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='operator',
        help_text='User role for access control'
    )
    
    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser
    
    @property
    def is_operator(self):
        return self.role == 'operator'
    
    @property
    def is_cook(self):
        return self.role == 'cook'

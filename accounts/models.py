from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        SUPER_ADMIN = 'super_admin', 'Super Admin'
        ORG_ADMIN   = 'org_admin',   'Org Admin'
        STAFF       = 'staff',       'Staff'
        CUSTOMER    = 'customer',    'Customer'

    role          = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    phone         = models.CharField(max_length=20, unique=True, null=True, blank=True)
    telegram_id   = models.BigIntegerField(unique=True, null=True, blank=True)
    language      = models.CharField(max_length=5, default='tg')  # tg, ru, en
    created_at    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

class Profile(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar     = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio        = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} — Profile"
from django.db import models
from accounts.models import User
import qrcode
import io
from django.core.files.base import ContentFile

class Organization(models.Model):
    class Plan(models.TextChoices):
        FREE       = 'free',       'Free'
        PRO        = 'pro',        'Pro'
        ENTERPRISE = 'enterprise', 'Enterprise'

    name       = models.CharField(max_length=255)
    slug       = models.SlugField(unique=True)
    owner      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organizations')
    plan       = models.CharField(max_length=20, choices=Plan.choices, default=Plan.FREE)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Branch(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='branches')
    name         = models.CharField(max_length=255)
    address      = models.TextField(blank=True)
    phone        = models.CharField(max_length=20, blank=True)
    is_active    = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.organization.name} — {self.name}"


class Window(models.Model):
    branch     = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='windows')
    name       = models.CharField(max_length=100)  # "Касса 1", "Кабинет 3"
    staff      = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='windows')
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.branch.name} — {self.name}"
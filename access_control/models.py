from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        CITIZEN = 'CITIZEN', 'Citizen'
        ORGANIZATION = 'ORGANIZATION', 'Organization'
        ADMIN = 'ADMIN', 'Administrator'
        OFFICER = 'OFFICER', 'Law Enforcement Officer'

    role = models.CharField(
        max_length=20, 
        choices=Role.choices, 
        default=Role.CITIZEN
    )
    
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    # Link to parent Organization if this user is a staff member
    organization = models.ForeignKey('OrganizationProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='staff_members')

    def is_citizen(self):
        return self.role == self.Role.CITIZEN
    
    def is_organization(self):
        return self.role == self.Role.ORGANIZATION
    
    def is_officer(self):
        return self.role == self.Role.OFFICER
    
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

class OrganizationProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='org_profile')
    organization_name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100, unique=True)
    website = models.URLField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.organization_name

class OfficerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='officer_profile')
    badge_number = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100)
    rank = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.rank} {self.user.get_full_name()}"

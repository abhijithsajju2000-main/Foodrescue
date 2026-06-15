from django.db import models

from django.contrib.auth.models import AbstractUser


class RoleChoices(models.TextChoices):
    
    DONOR = 'Donor', 'Donor'
    
    USER  = 'User',  'User'
    
    NGO   = 'NGO',   'NGO'
    
    ADMIN = 'Admin', 'Admin'


class Profile(AbstractUser):

    role    = models.CharField(max_length=10, choices=RoleChoices.choices, default=RoleChoices.USER)

    phone   = models.CharField(max_length=15, blank=True, null=True)

    address = models.TextField(blank=True, null=True)

    ngo_darpan_id    = models.CharField(max_length=50, blank=True, null=True, unique=True)

    organization_pan = models.CharField(max_length=10, blank=True, null=True, unique=True)

    is_verified      = models.BooleanField(default=False)

    class Meta:

        verbose_name        = 'Profile'

        verbose_name_plural = 'Profiles'


    def __str__(self):

        return f'{self.username} ({self.role})'
    
class OTP(models.Model):

    user = models.OneToOneField('Profile', on_delete=models.CASCADE)

    otp = models.CharField(max_length=4)

    otp_verified = models.BooleanField(default=False)

    class Meta:

        verbose_name = 'OTP'

        verbose_name_plural = 'OTPs'

    def __str__(self):

        return f'{self.user.username} OTP'
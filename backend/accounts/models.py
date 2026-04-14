from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    role = models.CharField(max_length=50, choices=[('DOCTOR', 'Doctor'), ('PATIENT', 'Patient'), ('ADMIN', 'Admin')], default='DOCTOR')
    hospital_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"

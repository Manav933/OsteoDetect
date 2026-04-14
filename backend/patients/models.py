import uuid
from django.db import models
from django.conf import settings

class Patient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient_profile', null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_patients')
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=20, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    contact_info = models.CharField(max_length=255, blank=True)
    
    # Baseline health info
    baseline_calcium_intake = models.CharField(max_length=50, default='Unknown')
    medical_history_notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['id']),
            models.Index(fields=['created_by']),
        ]
        
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


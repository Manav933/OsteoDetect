import uuid
from django.db import models
from patients.models import Patient
from django.conf import settings

class DiagnosisRecord(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Analysis'
        PROCESSING = 'PROCESSING', 'Processing'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'

    class RiskLevel(models.TextChoices):
        LOW = 'LOW', 'Low Risk'
        MEDIUM = 'MEDIUM', 'Medium Risk'
        HIGH = 'HIGH', 'High Risk'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='diagnoses')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    # Input Data - The 18 specific fields expected by the ML Modal
    xray_image = models.ImageField(upload_to='xrays/')
    identifier_1 = models.CharField(max_length=100, blank=True, null=True)
    spine_scandate = models.DateField(blank=True, null=True)
    spine_bmd = models.FloatField(blank=True, null=True)
    spine_tscore = models.FloatField(blank=True, null=True)
    hip_scandate = models.DateField(blank=True, null=True)
    hip_bmd = models.FloatField(blank=True, null=True)
    hip_tscore = models.FloatField(blank=True, null=True)
    hipneck_scandate = models.DateField(blank=True, null=True)
    hipneck_bmd = models.FloatField(blank=True, null=True)
    hipneck_tscore = models.FloatField(blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    age_category = models.CharField(max_length=50, blank=True, null=True)
    height = models.FloatField(blank=True, null=True)
    menopause_year = models.IntegerField(blank=True, null=True)
    smoking_status = models.CharField(max_length=50, blank=True, null=True)
    physical_activity_leval = models.CharField(max_length=50, blank=True, null=True)
    diet_plan = models.CharField(max_length=50, blank=True, null=True)
    alcohol_intake = models.CharField(max_length=50, blank=True, null=True)
    
    # Output Data
    pred_class = models.CharField(max_length=50, blank=True, null=True)
    confidence_score = models.FloatField(blank=True, null=True)
    risk_level = models.CharField(max_length=20, choices=RiskLevel.choices, blank=True, null=True)
    heatmap_image = models.ImageField(upload_to='heatmaps/', blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    error_message = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', 'created_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Diagnosis {self.id} for {self.patient}"

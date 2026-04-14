from django.contrib import admin

from .models import DiagnosisRecord


@admin.register(DiagnosisRecord)
class DiagnosisRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "doctor", "status", "risk_level", "created_at")
    list_filter = ("status", "risk_level", "created_at")
    search_fields = ("patient__first_name", "patient__last_name", "pred_class")
    readonly_fields = ("id", "created_at", "updated_at")

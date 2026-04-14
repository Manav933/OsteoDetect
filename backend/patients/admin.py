from django.contrib import admin

from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "created_by", "created_at")
    list_filter = ("gender", "created_at")
    search_fields = ("first_name", "last_name", "contact_info")
    readonly_fields = ("id", "created_at", "updated_at")

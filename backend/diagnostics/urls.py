from django.urls import path
from .views import (
    DashboardView,
    DiagnosisCreateWizardView,
    DiagnosisDetailView,
    PatientHistoryView,
    DiagnosisDeleteView,
    DiagnosisReportPdfView,
)

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('diagnose/new/', DiagnosisCreateWizardView.as_view(), name='diagnosis_create'),
    path('diagnose/<uuid:pk>/', DiagnosisDetailView.as_view(), name='diagnosis_detail'),
    path('diagnose/<uuid:pk>/report.pdf', DiagnosisReportPdfView.as_view(), name='diagnosis_report_pdf'),
    path('diagnose/<uuid:pk>/delete/', DiagnosisDeleteView.as_view(), name='diagnosis_delete'),
    path('patient/<uuid:pk>/history/', PatientHistoryView.as_view(), name='patient_history'),
]

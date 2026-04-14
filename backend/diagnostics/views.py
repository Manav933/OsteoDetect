from io import BytesIO

from django.shortcuts import redirect
from django.views.generic import DetailView, CreateView, TemplateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseNotAllowed
from django.db.models import Q
from django.http import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from .models import DiagnosisRecord
from patients.models import Patient
from .services.ml_client import MLClient
from .forms import DiagnosisForm

class DashboardView(LoginRequiredMixin, TemplateView):
    def get_template_names(self):
        if self.request.user.role == 'PATIENT':
            return ['diagnostics/patient_dashboard.html']
        return ['diagnostics/home.html']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        search_query = self.request.GET.get('q', '').strip()
        risk_filter = self.request.GET.get('risk', '').strip()
        context['ml_service_online'] = MLClient.health_check()
        context['search_query'] = search_query
        context['risk_filter'] = risk_filter
        
        if user.role == 'DOCTOR':
            patients_qs = Patient.objects.all().order_by('-created_at')
            diagnoses_qs = DiagnosisRecord.objects.select_related('patient', 'doctor').all().order_by('-created_at')
            if search_query:
                patients_qs = patients_qs.filter(
                    Q(first_name__icontains=search_query) | Q(last_name__icontains=search_query)
                )
                diagnoses_qs = diagnoses_qs.filter(
                    Q(patient__first_name__icontains=search_query)
                    | Q(patient__last_name__icontains=search_query)
                )
            if risk_filter in {'LOW', 'MEDIUM', 'HIGH'}:
                diagnoses_qs = diagnoses_qs.filter(risk_level=risk_filter)
            context['patients'] = patients_qs[:10]
            context['recent_diagnoses'] = diagnoses_qs[:10]
        elif user.role == 'PATIENT':
            try:
                patient_profile = user.patient_profile
                context['patient'] = patient_profile
                context['recent_diagnoses'] = DiagnosisRecord.objects.filter(patient=patient_profile).order_by('-created_at')[:5]
            except getattr(Patient, 'DoesNotExist', Exception):
                context['patient'] = None
                context['recent_diagnoses'] = []
        else:
            context['patients'] = Patient.objects.all().order_by('-created_at')[:5]
            context['recent_diagnoses'] = DiagnosisRecord.objects.all().order_by('-created_at')[:5]
                
        return context

class DiagnosisCreateWizardView(LoginRequiredMixin, CreateView):
    model = DiagnosisRecord
    form_class = DiagnosisForm
    template_name = 'diagnostics/wizard.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        user = self.request.user
        diagnosis = form.save(commit=False)
        diagnosis.doctor = user if user.role == 'DOCTOR' else None
        
        if user.role == 'PATIENT':
            try:
                patient = user.patient_profile
            except getattr(Patient, 'DoesNotExist', Exception):
                patient, _ = Patient.objects.get_or_create(
                    user=user, 
                    defaults={'first_name': user.first_name, 'last_name': user.last_name, 'created_by': user, 'date_of_birth': '2000-01-01', 'gender': 'O'}
                )
            diagnosis.patient = patient
        else:
            patient = form.cleaned_data.get('patient')
            if not patient:
                form.add_error('patient', 'Please select a patient for diagnosis.')
                return self.form_invalid(form)
            diagnosis.patient = patient
            
        diagnosis.save()
        MLClient.predict(diagnosis)
        
        return redirect('diagnosis_detail', pk=diagnosis.pk)

class DiagnosisDetailView(LoginRequiredMixin, DetailView):
    model = DiagnosisRecord
    template_name = 'diagnostics/result.html'
    context_object_name = 'diagnosis'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        if user.role == 'PATIENT' and obj.patient.user != user:
            raise PermissionDenied("You can only view your own records.")
        return obj

class PatientHistoryView(LoginRequiredMixin, DetailView):
    model = Patient
    template_name = 'diagnostics/history.html'
    context_object_name = 'patient'
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        if user.role == 'PATIENT' and obj.user != user:
            raise PermissionDenied("You can only view your own history.")
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        diagnoses = self.object.diagnoses.all().order_by('-created_at')
        context['diagnoses'] = diagnoses
        
        chrono_diagnoses = list(diagnoses.order_by('created_at'))
        labels = [d.created_at.strftime('%Y-%m-%d') for d in chrono_diagnoses if d.confidence_score]
        scores = [d.confidence_score for d in chrono_diagnoses if d.confidence_score]
        
        context['chart_labels'] = labels
        context['chart_data'] = scores
        
        if len(scores) >= 2:
            if scores[-1] > scores[-2] + 5.0: 
                context['risk_trend'] = 'worsening'
            elif scores[-1] < scores[-2] - 5.0:
                context['risk_trend'] = 'improving'
            else:
                context['risk_trend'] = 'stable'
        else:
            context['risk_trend'] = 'baseline'
            
        return context

class DiagnosisDeleteView(LoginRequiredMixin, DeleteView):
    model = DiagnosisRecord
    success_url = reverse_lazy('dashboard')
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        if user.role == 'PATIENT':
            if not getattr(obj, 'patient', None) or obj.patient.user != user:
                raise PermissionDenied("You can only delete your own records.")
        return obj

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(['POST'])


class DiagnosisReportPdfView(LoginRequiredMixin, DetailView):
    model = DiagnosisRecord

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        if user.role == 'PATIENT' and obj.patient.user != user:
            raise PermissionDenied("You can only export your own report.")
        return obj

    def render_to_response(self, context, **response_kwargs):
        diagnosis = self.object
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        y = height - 50

        lines = [
            "OsteoDetect Report",
            "",
            f"Record ID: {diagnosis.id}",
            f"Patient: {diagnosis.patient.first_name} {diagnosis.patient.last_name}",
            f"Doctor: {diagnosis.doctor or 'N/A'}",
            f"Created: {diagnosis.created_at.strftime('%Y-%m-%d %H:%M')}",
            "",
            f"Prediction Class: {diagnosis.pred_class or 'N/A'}",
            f"Confidence: {diagnosis.confidence_score or 'N/A'}%",
            f"Risk Level: {diagnosis.risk_level or 'N/A'}",
            "",
            "Clinical Explanation:",
            diagnosis.error_message or "No explanation available.",
            "",
            "This is an AI-based assistive tool, not a medical diagnosis.",
        ]

        for line in lines:
            pdf.drawString(50, y, str(line)[:110])
            y -= 18
            if y < 50:
                pdf.showPage()
                y = height - 50

        pdf.save()
        buffer.seek(0)
        filename = f"osteodetect-report-{diagnosis.id}.pdf"
        return FileResponse(buffer, as_attachment=True, filename=filename)

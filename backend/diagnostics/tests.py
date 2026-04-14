from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from accounts.models import User
from diagnostics.models import DiagnosisRecord
from patients.models import Patient


def make_test_image(name="scan.png"):
    image = Image.new("RGB", (64, 64), "white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


class DiagnosisAccessTests(TestCase):
    def setUp(self):
        self.doctor = User.objects.create_user(
            username="doctor1", password="testpass123", role="DOCTOR"
        )
        self.patient_user = User.objects.create_user(
            username="patient1", password="testpass123", role="PATIENT"
        )
        self.other_patient_user = User.objects.create_user(
            username="patient2", password="testpass123", role="PATIENT"
        )

        self.patient = Patient.objects.create(
            user=self.patient_user,
            created_by=self.patient_user,
            first_name="Alice",
            last_name="One",
            date_of_birth="1990-01-01",
            gender="F",
        )
        self.other_patient = Patient.objects.create(
            user=self.other_patient_user,
            created_by=self.other_patient_user,
            first_name="Bob",
            last_name="Two",
            date_of_birth="1988-01-01",
            gender="M",
        )
        self.record = DiagnosisRecord.objects.create(
            patient=self.other_patient,
            doctor=self.doctor,
            xray_image=make_test_image(),
            status=DiagnosisRecord.Status.COMPLETED,
            risk_level=DiagnosisRecord.RiskLevel.LOW,
            pred_class="Normal",
            confidence_score=92.0,
        )

    def test_patient_cannot_view_other_patient_record(self):
        self.client.login(username="patient1", password="testpass123")
        response = self.client.get(reverse("diagnosis_detail", kwargs={"pk": self.record.id}))
        self.assertEqual(response.status_code, 403)

    def test_doctor_can_view_record(self):
        self.client.login(username="doctor1", password="testpass123")
        response = self.client.get(reverse("diagnosis_detail", kwargs={"pk": self.record.id}))
        self.assertEqual(response.status_code, 200)

    def test_doctor_diagnosis_requires_selected_patient(self):
        self.client.login(username="doctor1", password="testpass123")
        response = self.client.post(
            reverse("diagnosis_create"),
            data={
                "identifier_1": "ID-01",
                "age_category": "Middle",
                "smoking_status": "Non-smoker",
                "physical_activity_leval": "Moderate",
                "diet_plan": "Normal",
                "alcohol_intake": "None",
                "xray_image": make_test_image("doctor.png"),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please select a patient for diagnosis.")

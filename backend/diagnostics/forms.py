from django import forms
from django.core.exceptions import ValidationError
from .models import DiagnosisRecord
from patients.models import Patient
import os

class DiagnosisForm(forms.ModelForm):
    patient = forms.ModelChoiceField(
        queryset=Patient.objects.none(),
        required=False,
        empty_label="Select patient",
    )

    class Meta:
        model = DiagnosisRecord
        fields = [
            'patient',
            'identifier_1',
            'spine_scandate', 'spine_bmd', 'spine_tscore',
            'hip_scandate', 'hip_bmd', 'hip_tscore',
            'hipneck_scandate', 'hipneck_bmd', 'hipneck_tscore',
            'birthdate', 'age_category', 'height', 'menopause_year',
            'smoking_status', 'physical_activity_leval', 'diet_plan', 'alcohol_intake',
            'xray_image'
        ]
        widgets = {
            'spine_scandate': forms.DateInput(attrs={'type': 'date'}),
            'hip_scandate': forms.DateInput(attrs={'type': 'date'}),
            'hipneck_scandate': forms.DateInput(attrs={'type': 'date'}),
            'birthdate': forms.DateInput(attrs={'type': 'date'}),
            'age_category': forms.Select(choices=[
                ('Young', 'Young (< 40)'),
                ('Middle', 'Middle (40-60)'),
                ('Senior', 'Senior (> 60)')
            ]),
            'smoking_status': forms.Select(choices=[
                ('Non-smoker', 'Non-smoker'),
                ('Former-smoker', 'Former Smoker'),
                ('Active-smoker', 'Active Smoker')
            ]),
            'physical_activity_leval': forms.Select(choices=[
                ('Sedentary', 'Sedentary'),
                ('Moderate', 'Moderate'),
                ('Active', 'Active')
            ]),
            'diet_plan': forms.Select(choices=[
                ('Normal', 'Normal'),
                ('Calcium-Rich', 'Calcium-Rich'),
                ('Vegan', 'Vegan')
            ]),
            'alcohol_intake': forms.Select(choices=[
                ('None', 'None'),
                ('Occasional', 'Occasional'),
                ('Frequent', 'Frequent')
            ]),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user and self.user.role == 'DOCTOR':
            self.fields['patient'].queryset = Patient.objects.all().order_by('first_name', 'last_name')
        else:
            self.fields['patient'].widget = forms.HiddenInput()

    def clean_xray_image(self):
        image = self.cleaned_data.get('xray_image', False)
        if image:
            if image.size > 5 * 1024 * 1024:
                raise ValidationError("Image file too large ( > 5mb )")
            ext = os.path.splitext(image.name)[1].lower()
            valid_extensions = ['.jpg', '.jpeg', '.png']
            if ext not in valid_extensions:
                raise ValidationError(f"Unsupported file extension. Allowed extensions: {', '.join(valid_extensions)}")
            return image
        else:
            raise ValidationError("Couldn't read uploaded image")

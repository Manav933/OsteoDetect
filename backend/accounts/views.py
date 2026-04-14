from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from patients.models import Patient

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=[('DOCTOR', 'Doctor'), ('PATIENT', 'Patient')])
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    
    # Optional fields for Doctor
    hospital_name = forms.CharField(max_length=255, required=False)

    # Optional fields for Patient mapping (minimal default, mostly done later)
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'hospital_name')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = form.cleaned_data.get('role')
            user.hospital_name = form.cleaned_data.get('hospital_name')
            user.save()

            if user.role == 'PATIENT':
                dob = form.cleaned_data.get('date_of_birth')
                gender = form.cleaned_data.get('gender')
                Patient.objects.create(
                    user=user,
                    created_by=user, # created by themselves
                    first_name=user.first_name,
                    last_name=user.last_name,
                    date_of_birth=dob if dob else '2000-01-01',
                    gender=gender if gender else 'O',
                )
            
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
        
    return render(request, 'registration/register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('dashboard')

def logout_view(request):
    logout(request)
    return redirect('login')

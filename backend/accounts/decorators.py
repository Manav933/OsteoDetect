from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def doctor_required(function=None, redirect_field_name='next', login_url=None):
    """
    Decorator for views that checks that the user is logged in and is a doctor,
    redirects to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and (u.role == 'DOCTOR' or u.is_superuser),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def patient_required(function=None, redirect_field_name='next', login_url=None):
    """
    Decorator for views that checks that the user is logged in and is a patient.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.role == 'PATIENT',
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

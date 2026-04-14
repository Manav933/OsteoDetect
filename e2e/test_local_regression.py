"""
Maps to LOCAL_REGRESSION_CHECKLIST.md (L-01 .. L-15).

Run from repo root:
  cd e2e
  ..\\backend\\venv\\Scripts\\python -m pip install -r requirements.txt
  ..\\backend\\venv\\Scripts\\python -m playwright install
  ..\\backend\\venv\\Scripts\\python -m pytest -q

Runnable without Playwright: test_live_server_responds"""

from __future__ import annotations

import urllib.error
import urllib.request

import pytest

# --- Always-on Django smoke (L-01-ish) ---


def test_live_server_responds(live_server, db):
    """Django test server starts; root URL returns a normal HTTP response."""
    url = live_server.url + "/"
    try:
        r = urllib.request.urlopen(url, timeout=10)
        assert r.status == 200
    except urllib.error.HTTPError as e:
        # LoginRequired redirect to login may surface as 302 in some clients;
        # urlopen follows redirects, so 200 is typical.
        assert e.code in (200, 302, 403)


# --- Playwright stubs: implement steps from checklist; un-skip when ready ---


@pytest.mark.e2e
@pytest.mark.skip(reason="Stub L-01/L-02: open homepage, register doctor (implement with Playwright)")
def test_L02_register_doctor(page, live_server):
    page.goto(live_server.url)
    # page.get_by_role("link", name="Register").click()
    # ... fill form, submit, assert doctor dashboard copy
    raise AssertionError("not implemented")


@pytest.mark.e2e
@pytest.mark.skip(reason="Stub L-03: register patient")
def test_L03_register_patient(page, live_server):
    raise AssertionError("not implemented")


@pytest.mark.e2e
@pytest.mark.skip(reason="Stub L-04: logout and assert protected route redirects")
def test_L04_logout(page, live_server):
    raise AssertionError("not implemented")


@pytest.mark.e2e
@pytest.mark.skip(reason="Stub L-05: doctor diagnosis happy path (ML must be running on :8000)")
def test_L05_doctor_diagnosis_happy_path(page, live_server):
    raise AssertionError("not implemented")


@pytest.mark.e2e
@pytest.mark.skip(reason="Stub L-06: patient diagnosis happy path")
def test_L06_patient_diagnosis_happy_path(page, live_server):
    raise AssertionError("not implemented")


@pytest.mark.e2e
@pytest.mark.skip(reason="Stub L-07: ML down → FAILED status (stop ML service for this run)")
def test_L07_ml_down_failed_status(page, live_server):
    raise AssertionError("not implemented")


@pytest.mark.e2e
@pytest.mark.skip(reason="Stub L-08: oversized / invalid file → form errors")
def test_L08_upload_validation(page, live_server):
    raise AssertionError("not implemented")


@pytest.mark.e2e
@pytest.mark.skip(reason="Stub L-09: patient A cannot open patient B diagnosis (403)")
def test_L09_patient_idor_detail(page, live_server):
    raise AssertionError("not implemented")


@pytest.mark.e2e
@pytest.mark.skip(reason="Stub L-10: patient opens own diagnosis")
def test_L10_patient_own_detail(page, live_server):
    raise AssertionError("not implemented")


@pytest.mark.e2e
@pytest.mark.skip(reason="Stub L-11: patient history page")
def test_L11_patient_history(page, live_server):
    raise AssertionError("not implemented")


@pytest.mark.e2e
@pytest.mark.skip(reason="Stub L-12: patient deletes own diagnosis")
def test_L12_delete_own(page, live_server):
    raise AssertionError("not implemented")


@pytest.mark.e2e
@pytest.mark.skip(reason="Stub L-13: patient cannot delete other's diagnosis")
def test_L13_delete_other_forbidden(page, live_server):
    raise AssertionError("not implemented")


@pytest.mark.e2e
@pytest.mark.skip(reason="Stub L-14: GET ML /health (use requests from test or assume ML external)")
def test_L14_ml_health_endpoint():
    # import requests
    # r = requests.get("http://127.0.0.1:8000/health", timeout=5)
    # assert r.status_code == 200
    raise AssertionError("not implemented")


@pytest.mark.e2e
@pytest.mark.skip(reason="Stub L-15: ML_SERVICE_URL env override (document or fix settings duplicate)")
def test_L15_ml_service_url_from_env():
    raise AssertionError("not implemented")

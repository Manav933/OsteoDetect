# OsteoDetect Deployment Guide

## Architecture
- Django app (`backend`) for authentication, dashboards, records, and reports.
- FastAPI app (`ml_service`) for ML inference endpoint (`/predict`).
- PostgreSQL for production database.
- Media storage for uploaded X-rays and heatmaps.

## Required Environment Variables

### Django (`backend/.env`)
- `SECRET_KEY=<strong-secret>`
- `DEBUG=False`
- `ALLOWED_HOSTS=your-domain.com`
- `DATABASE_URL=postgres://user:pass@host:5432/dbname`
- `ML_SERVICE_URL=https://your-ml-service-domain`

### ML Service
- Place model files where `ml_service/main.py` expects them:
  - `osteoporosis_multimodal_model_rmsprop_optimized.h5`
  - `preprocessing_objects_rmsprop_optimized.pkl`

## Local Production-like Run
1. Install dependencies:
   - `pip install -r backend/requirements.txt`
   - `pip install -r ml_service/requirements.txt`
2. Run migrations:
   - `cd backend`
   - `python manage.py migrate`
3. Collect static:
   - `python manage.py collectstatic --noinput`
4. Start ML service:
   - `cd ../ml_service`
   - `uvicorn main:app --host 0.0.0.0 --port 8000`
5. Start Django with gunicorn:
   - `cd ../backend`
   - `gunicorn config.wsgi:application --bind 0.0.0.0:8080`

## Render Deployment
- Create two services:
  1. Web service for Django.
  2. Web service for ML inference API.
- Add a managed PostgreSQL instance.
- Set Django `ML_SERVICE_URL` to ML service public URL.
- Enable persistent disk for media or configure external object storage.

## Security Checklist
- Keep `DEBUG=False`.
- Use strong `SECRET_KEY`.
- Restrict `ALLOWED_HOSTS`.
- Use HTTPS in production.
- Rotate credentials periodically.
- Monitor logs for failed authentication and ML errors.

## Basic Smoke Test
1. Register doctor and patient.
2. Doctor logs in, searches patient, creates diagnosis.
3. Patient logs in and views only own records.
4. Download PDF report from diagnosis page.

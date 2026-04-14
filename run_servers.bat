@echo off
echo Starting Osteoporosis Detection Platform Services...

:: Ensure .env exists in backend
if not exist "backend\.env" (
    echo Creating backend\.env file from .env.example...
    copy "backend\.env.example" "backend\.env"
)

:: Start ML Service in a new window
echo Starting ML FastAPI Service...
start "ML Service" cmd /k "cd ml_service && call venv\Scripts\activate && python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"


:: Wait a few seconds for ML service to boot
timeout /t 3 >nul

:: Migrate and Start Django Web Server in a new window
echo Starting Django Web Server...
start "Django Server" cmd /k "cd backend && call venv\Scripts\activate && python manage.py makemigrations accounts patients diagnostics && python manage.py migrate && python manage.py runserver 8080"

echo Both services have been started in separate windows!
echo Access the Dashboard at: http://127.0.0.1:8080
pause

@echo off
echo ============================================
echo  SmartBook - Setup Script
echo ============================================

echo.
echo [1/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [2/4] Running migrations...
python manage.py migrate

echo.
echo [3/4] Seeding demo data...
python seed_data.py

echo.
echo [4/4] Starting development server...
echo.
echo  Visit: http://127.0.0.1:8000
echo  Admin: http://127.0.0.1:8000/admin
echo.
echo  Credentials:
echo    Admin:    admin / Admin@1234
echo    Provider: dr_sarah / Provider@1234
echo    User:     john_doe / User@1234
echo.
python manage.py runserver

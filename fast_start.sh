@echo off
echo 🚀 Iniciando aplicación...

REM Crear ventana para backend
echo 📡 Iniciando backend (FastAPI)...
start "Backend - FastAPI" cmd /k "cd fast && venv\Scripts\activate && uvicorn app.main:app --port 3000 --reload"

REM Esperar 2 segundos
timeout /t 2 /nobreak >nul

REM Crear ventana para frontend
echo 🌐 Iniciando frontend (React)...
start "Frontend - React" cmd /k "cd front && npm run dev"

echo ✅ Ambos servicios iniciados en ventanas separadas!
echo 📡 Backend: http://localhost:3000
echo 🌐 Frontend: http://localhost:5173
echo.
echo Cierra las ventanas correspondientes para detener cada servicio.
pause
@echo off
REM Script batch para iniciar el backend con webhook y ngrok
REM Uso: start_with_webhook.bat

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════╗
echo ║  Pizzeria Bot - Iniciando con WEBHOOK     ║
echo ╚════════════════════════════════════════════╝
echo.

REM 1. Verificar que ngrok está instalado
echo 🔍 Verificando ngrok...
where ngrok >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ ngrok no encontrado. Descárgalo desde: https://ngrok.com
    exit /b 1
)
echo ✅ ngrok encontrado

REM 2. Activar el entorno virtual Python
echo.
echo 🐍 Activando entorno virtual Python...
call env\Scripts\activate.bat

REM 3. Iniciar ngrok en background
echo.
echo 🚀 Iniciando ngrok en puerto 5000...
start /min ngrok http 5000

REM Esperar a que ngrok se inicie
echo ⏳ Esperando a que ngrok se inicie (3 segundos)...
timeout /t 3 /nobreak

REM 4. Iniciar el backend
echo.
echo 🍕 Iniciando Backend (Flask + Telegram Bot)...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

set USE_WEBHOOK=true

cd pizzeria_backend
python run.py

echo.
echo Application closed
pause

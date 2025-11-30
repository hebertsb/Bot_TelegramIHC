# Script PowerShell para iniciar el backend con webhook y ngrok
# Uso: .\start_with_webhook.ps1

Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Pizzeria Bot - Iniciando con WEBHOOK     ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar que ngrok está instalado
Write-Host "🔍 Verificando ngrok..." -ForegroundColor Yellow
try {
    ngrok --version | Out-Null
    Write-Host "✅ ngrok encontrado" -ForegroundColor Green
} catch {
    Write-Host "❌ ngrok no encontrado. Descárgalo desde: https://ngrok.com" -ForegroundColor Red
    exit 1
}

# 2. Activar el entorno virtual Python
Write-Host ""
Write-Host "🐍 Activando entorno virtual Python..." -ForegroundColor Yellow
& ".\env\Scripts\Activate.ps1"

# 3. Iniciar ngrok en background en otra ventana
Write-Host ""
Write-Host "🚀 Iniciando ngrok en puerto 5000..." -ForegroundColor Yellow
Start-Process -FilePath "ngrok" -ArgumentList "http 5000" -WindowStyle Minimized

# Esperar a que ngrok se inicie
Write-Host "⏳ Esperando a que ngrok se inicie (3 segundos)..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# 4. Obtener la URL de ngrok
Write-Host ""
Write-Host "🔗 Obteniendo URL de ngrok..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:4040/api/tunnels" -UseBasicParsing
    $data = $response.Content | ConvertFrom-Json
    $ngrok_url = $data.tunnels[0].public_url
    Write-Host "✅ URL de ngrok: $ngrok_url" -ForegroundColor Green
} catch {
    Write-Host "⚠️  No se pudo obtener la URL de ngrok automáticamente" -ForegroundColor Yellow
    Write-Host "Verifica que ngrok esté ejecutándose en otro terminal" -ForegroundColor Yellow
    $ngrok_url = "http://localhost:5000"
}

# 5. Iniciar el backend
Write-Host ""
Write-Host "🍕 Iniciando Backend (Flask + Telegram Bot)..." -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# Establecer variables de entorno
$env:USE_WEBHOOK = "true"
$env:NGROK_URL = $ngrok_url

# Ejecutar el servidor
cd pizzeria_backend
python run.py

Write-Host ""
Write-Host "Application closed" -ForegroundColor Yellow

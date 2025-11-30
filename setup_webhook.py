#!/usr/bin/env python3
# Script para configurar fácilmente el webhook

import os
import sys

def setup_webhook():
    """Asistente interactivo para configurar webhook"""
    
    print("\n" + "="*60)
    print("⚙️  CONFIGURADOR DE WEBHOOK - Pizzeria Bot")
    print("="*60 + "\n")
    
    print("Elige el método de conexión:\n")
    print("1️⃣  ngrok (Desarrollo/Testing) - URL pública temporal")
    print("2️⃣  Dominio personalizado (Producción) - HTTPS permanente")
    print("3️⃣  Polling local (Sin webhook) - Para testing local\n")
    
    choice = input("Selecciona (1, 2 o 3): ").strip()
    
    if choice == "1":
        setup_ngrok()
    elif choice == "2":
        setup_custom_domain()
    elif choice == "3":
        setup_polling()
    else:
        print("❌ Opción inválida")
        sys.exit(1)

def setup_ngrok():
    """Configurar para usar ngrok"""
    print("\n" + "-"*60)
    print("🚀 Configurando ngrok...")
    print("-"*60 + "\n")
    
    print("✅ ngrok será iniciado automáticamente")
    print("📌 La URL se obtiene dinámicamente")
    print("\nPara ejecutar:")
    print("  PowerShell: .\\start_with_webhook.ps1")
    print("  CMD:        start_with_webhook.bat\n")
    
    env_file = "pizzeria_backend/.env"
    create_env_file(env_file, {
        "USE_WEBHOOK": "true",
        "WEBHOOK_URL": "http://localhost:5000",  # Se sobrescribe en run.py
        "WEBHOOK_SECRET_TOKEN": "ngrok_default_token_123"
    })
    
    print(f"✅ Archivo {env_file} creado")
    print("Listo para usar ngrok!\n")

def setup_custom_domain():
    """Configurar para usar dominio personalizado"""
    print("\n" + "-"*60)
    print("🌐 Configurando Dominio Personalizado...")
    print("-"*60 + "\n")
    
    domain = input("Ingresa tu dominio (ej: tu-dominio.com): ").strip()
    if not domain:
        print("❌ Dominio vacío")
        return
    
    # Asegurar HTTPS
    if not domain.startswith("https://"):
        domain = f"https://{domain}"
    
    token = input("\nIngresa token secreto (o presiona Enter para generar): ").strip()
    if not token:
        import secrets
        token = secrets.token_urlsafe(32)
        print(f"✅ Token generado: {token}")
    
    print("\n" + "="*60)
    print("⚙️  CONFIGURACIÓN FINAL")
    print("="*60)
    print(f"Dominio: {domain}")
    print(f"Token: {token[:20]}... (guardado securo)")
    print(f"Path: /telegram/webhook\n")
    
    env_file = "pizzeria_backend/.env"
    create_env_file(env_file, {
        "USE_WEBHOOK": "true",
        "WEBHOOK_URL": domain,
        "WEBHOOK_SECRET_TOKEN": token
    })
    
    print(f"✅ Archivo {env_file} actualizado")
    print("\n📝 PRÓXIMOS PASOS:")
    print("1. Configura Nginx/Apache como reverse proxy")
    print("2. Obtén certificado SSL (Let's Encrypt o CloudFlare)")
    print("3. Ejecuta: python pizzeria_backend/run.py")
    print("4. Verifica logs para confirmar webhook registrado\n")

def setup_polling():
    """Configurar para usar polling (sin webhook)"""
    print("\n" + "-"*60)
    print("📡 Configurando Polling (Sin Webhook)...")
    print("-"*60 + "\n")
    
    print("✅ El bot usará polling (preguntará a Telegram cada 30s)")
    print("📌 No requiere URL pública ni certificado SSL")
    print("⚠️  No es recomendado para producción\n")
    
    env_file = "pizzeria_backend/.env"
    create_env_file(env_file, {
        "USE_WEBHOOK": "false",
        "WEBHOOK_URL": "http://localhost:5000",
        "WEBHOOK_SECRET_TOKEN": "polling_no_needed"
    })
    
    print(f"✅ Archivo {env_file} creado")
    print("Para ejecutar:")
    print("  cd pizzeria_backend")
    print("  python run.py\n")

def create_env_file(filepath, config):
    """Crear archivo .env con la configuración"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    content = "# Configuración del Webhook - Auto-generado\n\n"
    for key, value in config.items():
        content += f"{key}={value}\n"
    
    with open(filepath, 'w') as f:
        f.write(content)

def show_current_config():
    """Mostrar configuración actual"""
    print("\n" + "="*60)
    print("📋 CONFIGURACIÓN ACTUAL")
    print("="*60 + "\n")
    
    env_file = "pizzeria_backend/.env"
    
    if not os.path.exists(env_file):
        print(f"❌ No se encontró {env_file}")
        print("Ejecuta este script para crear la configuración\n")
        return
    
    print(f"📄 Contenido de {env_file}:\n")
    with open(env_file, 'r') as f:
        content = f.read()
        print(content)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--show":
        show_current_config()
    else:
        setup_webhook()

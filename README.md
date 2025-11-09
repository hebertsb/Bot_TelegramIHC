# 🤖 Pizzería Nova - Bot de Pedidos en Telegram

¡Bienvenido al repositorio de Pizzería Nova! Este proyecto es un sistema completo para gestionar pedidos de una pizzería a través de un bot de Telegram, integrando una aplicación web interactiva para una experiencia de usuario fluida y un panel de administración para el personal del restaurante.

## ✨ Características Principales

- **Interfaz de Bot en Telegram**: Comandos simples (`/start`, `/mispedidos`) para interactuar con los clientes.
- **Aplicación Web Integrada**: Los usuarios realizan sus pedidos en una aplicación web moderna y amigable que se abre directamente desde el chat de Telegram.
- **Menú Dinámico**: El menú se carga desde el backend, permitiendo cambios de precios y productos sin necesidad de modificar el código del frontend.
- **Creación de Pizzas con IA**: Una función creativa que utiliza la API de Google Gemini para sugerir nombres y descripciones de pizzas basadas en los ingredientes seleccionados por el usuario.
- **Base de Datos en Tiempo Real**: Todos los pedidos se guardan y gestionan en Google Firestore, permitiendo persistencia y escalabilidad.
- **Notificaciones Automatizadas**:
    - **Para el Cliente**: Recibe una factura de confirmación instantánea en Telegram al realizar el pedido y notificaciones sobre cada cambio de estado (Confirmado, En preparación, En camino, etc.).
    - **Para el Restaurante**: Se envía una alerta a un chat de Telegram designado para el personal con los detalles de cada nuevo pedido.
- **Panel de Administración Web**: Una interfaz (`admin.html`) para que el personal del restaurante pueda ver todos los pedidos y actualizar su estado con un solo clic.
- **Facturación Automática**: Generación de facturas en formato HTML accesibles a través de un enlace.

## 🛠️ Tecnologías Utilizadas

- **Backend**:
    - **Lenguaje**: Python 3
    - **Framework**: Flask
    - **Bot de Telegram**: `python-telegram-bot`
    - **Inteligencia Artificial**: Google Generative AI (Gemini)
- **Base de Datos**:
    - Google Firestore (NoSQL)
- **Frontend**:
    - HTML5
    - CSS3
    - JavaScript (Vanilla)
- **Alojamiento (Sugerido)**:
    - **Backend**: Cualquier servicio que soporte aplicaciones Python (Heroku, PythonAnywhere, un VPS).
    - **Frontend**: Netlify, Vercel, o GitHub Pages para alojar los archivos estáticos (`index.html`, `admin.html`).

## 📁 Estructura del Proyecto

```
/
├── pizzeria_backend/         # Contiene toda la lógica del servidor Flask
│   ├── app/                  # Módulos de la aplicación (rutas, servicios, bot)
│   ├── config.py             # Archivo de configuración (API Keys, etc.)
│   ├── requirements.txt      # Dependencias de Python
│   └── run.py                # Punto de entrada para iniciar el servidor
├── index.html                # La aplicación web para clientes
├── admin.html                # El panel de administración para el restaurante
└── README.md                 # Este archivo
```

## 🚀 Instalación y Puesta en Marcha

Sigue estos pasos para configurar y ejecutar el proyecto en un entorno local.

### Prerrequisitos

- Python 3.8 o superior.
- Una cuenta de Firebase con un proyecto y la base de datos Firestore activada.
- Un bot de Telegram y su respectivo **Token**.
- Una **API Key** de Google Gemini.

### 1. Configuración del Backend

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/hebertsb/Bot_TelegramIHC.git
    cd Bot_TelegramIHC
    ```

2.  **Crea y activa un entorno virtual:**
    ```bash
    # En Windows
    python -m venv venv
    .\venv\Scripts\activate

    # En macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instala las dependencias de Python:**
    ```bash
    pip install -r pizzeria_backend/requirements.txt
    ```

4.  **Configura las variables de entorno:**
    - Dentro de la carpeta `pizzeria_backend/`, renombra el archivo de credenciales de Firebase que descargaste a `pizzeriabackend-firebase-adminsdk-fbsvc-f65e1c0eb7.json` (o actualiza la ruta en `config.py`).
    - Edita el archivo `pizzeria_backend/config.py` y añade tus claves y URLs. **¡NUNCA subas este archivo con tus claves a un repositorio público!**

    ```python
    # pizzeria_backend/config.py

    # Token de tu bot de Telegram
    TELEGRAM_BOT_TOKEN = "TU_TELEGRAM_BOT_TOKEN"

    # URL donde alojarás tu index.html (ej. Netlify)
    WEB_APP_URL = "https://tu-url-de-netlify.netlify.app"

    # ID del chat de Telegram del restaurante para recibir notificaciones de nuevos pedidos
    RESTAURANT_CHAT_ID = "ID_DEL_CHAT_DEL_RESTAURANTE"

    # Ruta al archivo de credenciales de Firebase
    FIREBASE_KEY_PATH = "pizzeria_backend/pizzeriabackend-firebase-adminsdk-fbsvc-f65e1c0eb7.json"

    # API Key de Google Gemini
    GEMINI_API_KEY = "TU_API_KEY_DE_GEMINI"

    # URL de una imagen para el mensaje de bienvenida del bot
    IMAGE_URL = "https://ejemplo.com/imagen_pizza.jpg"
    ```

5.  **Ejecuta el servidor backend:**
    ```bash
    python pizzeria_backend/run.py
    ```
    Por defecto, el servidor se ejecutará en `http://127.0.0.1:5000`.

### 2. Configuración del Frontend

1.  **Aloja `index.html`**:
    - Sube el archivo `index.html` a un servicio de hosting estático como Netlify.
    - Asegúrate de que la URL que te proporciona Netlify sea la misma que configuraste en `WEB_APP_URL` en el `config.py` del backend.

2.  **Usa el Panel de Administración**:
    - El archivo `admin.html` es autocontenido. Simplemente ábrelo en tu navegador web.
    - Este panel hará peticiones a tu backend (que debe estar en ejecución) para cargar y actualizar los pedidos.

## 🌊 Flujo de Trabajo del Sistema

1.  **Inicio**: Un usuario encuentra tu bot en Telegram y envía el comando `/start`.
2.  **Pedido**: El bot responde con un mensaje de bienvenida y un botón para "Hacer Mi Pedido". Al tocarlo, se abre la aplicación web (`index.html`).
3.  **Construcción del Pedido**: El cliente navega por el menú, añade productos al carrito y, si lo desea, usa la función de IA para crear una pizza personalizada.
4.  **Envío**: El cliente introduce su dirección y método de pago, y envía el pedido.
5.  **Procesamiento**:
    - El frontend envía los datos del pedido al endpoint `/submit_order` del backend.
    - El backend guarda el pedido en Firestore.
    - El backend envía una factura de confirmación al chat del cliente en Telegram.
    - El backend envía una alerta de "Nuevo Pedido" al chat del restaurante.
6.  **Gestión**:
    - El personal del restaurante abre `admin.html` y ve el nuevo pedido.
    - A medida que el pedido avanza (de "Confirmado" a "En preparación", etc.), el personal actualiza el estado en el panel.
    - El panel llama al endpoint `/update_status` del backend.
7.  **Notificación de Estado**: El backend recibe la actualización, la guarda en Firestore y envía una notificación al cliente informándole del nuevo estado de su pedido.
8.  **Finalización**: El ciclo termina cuando el pedido es "Entregado".

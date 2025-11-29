# Guía de Integración Backend - Pizzería Nova

Esta documentación técnica describe el funcionamiento completo del backend desplegado en Railway, incluyendo endpoints, formatos de datos, estados de pedidos y el flujo de notificaciones automáticas vía Telegram.

**Base URL (Producción):** `https://bottelegramihc-production.up.railway.app`

---

## 1. Endpoints Públicos (Frontend WebApp)

Estos son los endpoints que la WebApp (React/JS) debe consumir.

### 1.1. Obtener Menú Completo
Recupera el catálogo de productos organizado por categorías.

*   **Endpoint:** `/get_products`
*   **Método:** `GET`
*   **Respuesta (200 OK):**
    ```json
    {
        "promociones": [
            {
                "id": "promo-1",
                "name": "Combo Pizza + Coca-Cola",
                "description": "...",
                "price": 11.00,
                "emoji": "🔥",
                "image": "https://..."
            }
        ],
        "pizzas": [...],
        "bebidas": [...],
        "postres": [...],
        "adicionales": [...]
    }
    ```

### 1.2. Enviar Pedido (Checkout)
Procesa el pedido, lo guarda en Firebase y dispara las notificaciones.

*   **Endpoint:** `/submit_order`
*   **Método:** `POST`
*   **Headers:** `Content-Type: application/json`
*   **Payload Requerido (Actualizado):**
    ```json
    {
        "chat_id": "123456789",  // CRÍTICO: ID de Telegram del usuario (WebApp.initDataUnsafe.user.id)
        "order": {
            "id": "ORD-171...",          // ID único generado por el frontend
            "total": 150.50,
            "items": [
                {
                    "id": "pizza-1",
                    "name": "Pizza Pepperoni",
                    "price": 50.00,
                    "quantity": 2,
                    "emoji": "🍕"
                }
            ],
            "address": "Calle Falsa 123",
            "location": {                // Opcional (puede ser null si falla el GPS)
                "latitude": -17.123,
                "longitude": -63.123
            },
            "paymentMethod": "QR",       // "QR" o "Efectivo"
            "date": "2024-05-20T10:30:00Z", // Fecha ISO
            "date_ts": 1716197400000,    // Nuevo: Timestamp en milisegundos (Date.now())
            "channel": "telegram_webapp",// Nuevo: Identificador del canal
            "currency": "Bs",            // Nuevo: Moneda
            "status": "Pendiente",       // Estado inicial
            "isRated": false             // Nuevo: Control de valoración
        }
    }
    ```
*   **Acciones del Backend al recibir esto:**
    1.  Guarda el pedido completo (incluyendo los nuevos campos) en **Firestore**.
    2.  Envía una **Factura (Texto + Botón)** al chat privado del cliente en Telegram.
    3.  Envía una **Alerta de Nuevo Pedido** al chat del Restaurante.

### 1.3. Generar Idea de Pizza (IA)
Usa Google Gemini para crear una pizza personalizada.

*   **Endpoint:** `/generate_pizza_idea`
*   **Método:** `POST`
*   **Payload:** `{"ingredients": ["piña", "jamón", "jalapeños"]}`
*   **Respuesta:** `{"name": "...", "description": "..."}`

### 1.4. Ver Factura Web
Renderiza una vista HTML de la factura.

*   **Endpoint:** `/factura/<order_id>`
*   **Método:** `GET`
*   **Uso:** Este enlace se genera automáticamente y se envía al usuario por Telegram.

### 1.5. Geocodificación Inversa (Proxy)
Convierte coordenadas (latitud/longitud) en una dirección legible. Úsalo para evitar problemas de CORS con Nominatim.

*   **Endpoint:** `/reverse_geocode`
*   **Método:** `GET`
*   **Parámetros URL:** `?lat=-17.78&lon=-63.18`
*   **Respuesta (200 OK):**
    ```json
    {
        "display_name": "Calle Falsa 123, Santa Cruz de la Sierra, Bolivia",
        "raw": { ... } // Datos crudos de Nominatim
    }
    ```

---

## 2. Endpoints Administrativos (Gestión de Pedidos)

Estos endpoints permiten gestionar el ciclo de vida del pedido.

### 2.1. Actualizar Estado del Pedido
Cambia el estado de un pedido y notifica al cliente.

*   **Endpoint:** `/update_status/<order_id>`
*   **Método:** `POST`
*   **Payload:** `{"status": "Nuevo Estado"}`
*   **Estados Soportados y Notificaciones:**
    El backend reconoce estos estados y envía mensajes automáticos al cliente:
    *   `"Confirmado"` -> "✅ ¡Tu pedido ha sido confirmado!"
    *   `"En preparación"` -> "👨‍🍳 ¡Estamos preparando tu pedido!"
    *   `"En camino"` -> "🛵 ¡Tu pedido ya está en camino!"
    *   `"Entregado"` -> "🎉 ¡Tu pedido ha sido entregado!"
    *   `"Cancelado"` -> "❌ Tu pedido ha sido cancelado."

### 2.2. Obtener Todos los Pedidos
*   **Endpoint:** `/get_orders`
*   **Método:** `GET`
*   **Respuesta:** Lista de todos los pedidos almacenados en Firestore.

---

## 3. Flujo de Notificaciones (Telegram)

El backend actúa como un puente entre la WebApp y el Chat de Telegram.

1.  **Cliente -> WebApp:** El usuario arma su carrito y confirma.
2.  **WebApp -> Backend (`/submit_order`):** Envía los datos JSON.
3.  **Backend -> Telegram (Cliente):**
    *   El bot envía inmediatamente un mensaje al usuario:
        > **🍕 Pizzeria Nova - Factura 🍕**
        > ...detalles del pedido...
        > [Botón: Ver Factura Web 🧾]
4.  **Backend -> Telegram (Restaurante):**
    *   El bot envía una alerta al grupo/chat del restaurante con los detalles para preparar la orden.

---

## 4. Notas para el Desarrollador Frontend

*   **`chat_id` es vital:** Sin este campo en el JSON de `/submit_order`, el backend no sabrá a quién enviar la confirmación y fallará (o devolverá error 400). Asegúrate de obtenerlo del contexto de Telegram WebApp.
*   **CORS:** Habilitado para cualquier origen (`*`), no deberías tener bloqueos.
*   **Manejo de Errores:** Siempre verifica el `status` en la respuesta JSON. Si es `error`, muestra el `message` al usuario.

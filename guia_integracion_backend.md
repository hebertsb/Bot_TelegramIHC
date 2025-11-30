# Guía de Integración Backend - Pizzería Nova

Esta documentación técnica describe el funcionamiento completo del backend desplegado en Railway, incluyendo endpoints, formatos de datos, estados de pedidos y el flujo de notificaciones automáticas vía Telegram.

**Base URL (Producción):** `https://bottelegramihc-production.up.railway.app`

> [!NOTE]
> **Modo Simulación Desactivado:** La simulación automática de estados ha sido desactivada para permitir el control manual por parte de los repartidores a través de la App de Delivery. El flujo ahora depende de las interacciones reales del conductor.

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
Procesa el pedido, lo guarda en Firebase y dispara las notificaciones. **Intenta asignar automáticamente un conductor disponible.**

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
    1.  Guarda el pedido completo en **Firestore**.
    2.  Envía una **Factura** al chat privado del cliente.
    3.  Envía una **Alerta** al chat del Restaurante.
    4.  **Asignación:** Busca conductores activos (`status="disponible"`) y asigna el pedido al primero encontrado (o al más cercano en futuras versiones).

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

### 1.5. Geocodificación Inversa (Proxy)
Convierte coordenadas en dirección legible.

*   **Endpoint:** `/reverse_geocode`
*   **Método:** `GET`
*   **Parámetros:** `?lat=...&lon=...`

---

## 2. Endpoints para Conductores (App Delivery)

Estos endpoints son exclusivos para la aplicación de los repartidores.

### 2.1. Actualizar Ubicación (Fake GPS)
Envía la ubicación en tiempo real del conductor.

*   **Endpoint:** `/driver/location`
*   **Método:** `POST`
*   **Payload:**
    ```json
    {
        "driver_id": "D1",
        "latitude": -17.7833,
        "longitude": -63.1821
    }
    ```

### 2.2. Obtener Mis Pedidos
Obtiene los pedidos asignados a un conductor específico.

*   **Endpoint:** `/driver/orders/<driver_id>`
*   **Método:** `GET`
*   **Respuesta:** Lista de objetos `order`.

### 2.3. Aceptar Pedido
El conductor confirma que realizará la entrega.

*   **Endpoint:** `/driver/accept`
*   **Método:** `POST`
*   **Payload:** `{"order_id": "ORD-123", "driver_id": "D1"}`
*   **Efecto:** Cambia estado a `Repartidor Asignado` y notifica al cliente.

### 2.4. Recoger Pedido
El conductor recoge el pedido del restaurante.

*   **Endpoint:** `/driver/pickup`
*   **Método:** `POST`
*   **Payload:** `{"order_id": "ORD-123"}`
*   **Efecto:** Cambia estado a `En camino` y notifica al cliente.

### 2.5. Entregar Pedido
El conductor entrega el pedido al cliente.

*   **Endpoint:** `/driver/deliver`
*   **Método:** `POST`
*   **Payload:** `{"order_id": "ORD-123"}`
*   **Efecto:** Cambia estado a `Entregado` y notifica al cliente.

---

## 3. Endpoints Administrativos (Gestión de Pedidos)

### 3.1. Actualizar Estado del Pedido (Manual/Admin)
Cambia el estado de un pedido y notifica al cliente.

*   **Endpoint:** `/update_status/<order_id>`
*   **Método:** `POST`
*   **Payload:** `{"status": "Nuevo Estado"}`

### 3.2. Obtener Todos los Pedidos
*   **Endpoint:** `/get_orders`
*   **Método:** `GET`

### 3.3. Rastrear Pedido Individual (Polling)
Para mostrar el estado en tiempo real en el Frontend.

*   **Endpoint:** `/get_order/<order_id>`
*   **Método:** `GET`
*   **Respuesta:** Incluye `status` y `driver_location` si está disponible.

---

## 4. Flujo de Notificaciones (Automático)

1.  **Confirmación:** "✅ ¡Tu pedido ha sido confirmado!"
2.  **Repartidor Asignado:** "🛵 ¡Un repartidor ha aceptado tu pedido!"
3.  **En Camino:** "🚀 ¡Tu pedido ya está en camino!"
4.  **Entregado:** "🎉 ¡Tu pedido ha sido entregado!"

El backend actúa como orquestador entre la WebApp, la App de Delivery y el Chat de Telegram.

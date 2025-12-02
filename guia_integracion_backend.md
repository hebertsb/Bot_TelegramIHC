# Guía de Integración Backend - Pizzería Nova

Esta documentación técnica describe el funcionamiento completo del backend desplegado en Railway, incluyendo endpoints, formatos de datos, estados de pedidos y el flujo de notificaciones automáticas vía Telegram.

**Base URL (Producción):** `https://bottelegramihc-production.up.railway.app`

> [!NOTE] > **Modo Simulación Desactivado:** La simulación automática de estados ha sido desactivada para permitir el control manual por parte de los repartidores a través de la App de Delivery. El flujo ahora depende de las interacciones reales del conductor.

---

## 1. Endpoints Públicos (Frontend WebApp)

Estos son los endpoints que la WebApp (React/JS) debe consumir.

### 1.1. Obtener Menú Completo

Recupera el catálogo de productos organizado por categorías.

- **Endpoint:** `/get_products`
- **Método:** `GET`
- **Respuesta (200 OK):**
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

- **Endpoint:** `/submit_order`
- **Método:** `POST`
- **Headers:** `Content-Type: application/json`
- **Payload Requerido (Actualizado):**
  ```json
  {
    "chat_id": "123456789", // CRÍTICO: ID de Telegram del usuario (WebApp.initDataUnsafe.user.id)
    "order": {
      "id": "ORD-171...", // ID único generado por el frontend
      "total": 150.5,
      "items": [
        {
          "id": "pizza-1",
          "name": "Pizza Pepperoni",
          "price": 50.0,
          "quantity": 2,
          "emoji": "🍕"
        }
      ],
      "address": "Calle Falsa 123",
      "location": {
        // Opcional (puede ser null si falla el GPS)
        "latitude": -17.123,
        "longitude": -63.123
      },
      "paymentMethod": "QR", // "QR" o "Efectivo"
      "date": "2024-05-20T10:30:00Z", // Fecha ISO
      "date_ts": 1716197400000, // Nuevo: Timestamp en milisegundos (Date.now())
      "channel": "telegram_webapp", // Nuevo: Identificador del canal
      "currency": "Bs", // Nuevo: Moneda
      "status": "Pendiente", // Estado inicial
      "isRated": false // Nuevo: Control de valoración
    }
  }
  ```
- **Acciones del Backend al recibir esto:**
  1.  Guarda el pedido completo en **Firestore**.
  2.  Envía una **Factura** al chat privado del cliente.
  3.  Envía una **Alerta** al chat del Restaurante.
  4.  **Asignación Inteligente:**
      - Busca conductores activos (`status="disponible"`).
      - Calcula la distancia de cada conductor al restaurante.
      - Asigna el pedido **exclusivamente al conductor más cercano**.
      - Si no hay conductores con ubicación reciente, asigna al primero disponible o deja pendiente.

### 1.3. Generar Idea de Pizza (IA)

Usa Google Gemini para crear una pizza personalizada.

- **Endpoint:** `/generate_pizza_idea`
- **Método:** `POST`
- **Payload:** `{"ingredients": ["piña", "jamón", "jalapeños"]}`
- **Respuesta:** `{"name": "...", "description": "..."}`

### 1.4. Calificar Pedido (Nuevo)

Permite al cliente enviar una valoración del servicio una vez que el pedido ha sido entregado.

- **Endpoint:** `/api/rate_order`
- **Método:** `POST`
- **Headers:** `Content-Type: application/json`
- **Payload:**
  ```json
  {
    "order_id": "ORD-1764661802983-8602",
    "restaurant_rating": 5, // Entero 1-5
    "delivery_rating": 4, // Entero 1-5
    "comment": "Excelente servicio, llegó muy rápido." // Opcional
  }
  ```
- **Respuesta (200 OK):**
  ```json
  {
    "status": "success",
    "message": "Calificación guardada correctamente"
  }
  ```
  > **Nota sobre Notificaciones:** Al recibir una calificación exitosa, el Backend automáticamente:
  > 1. Guarda los datos en el documento del pedido en Firebase (`rating` field).
  > 2. Envía una notificación inmediata vía Telegram al **Restaurante** con el detalle de estrellas y comentario.
  > 3. Envía una notificación inmediata vía Telegram al **Conductor** asignado (si tiene chat_id registrado) felicitándolo o informándole del feedback.

### 1.5. Ver Factura Web

Renderiza una vista HTML de la factura.

- **Endpoint:** `/factura/<order_id>`
- **Método:** `GET`

### 1.5. Geocodificación Inversa (Proxy)

Convierte coordenadas en dirección legible.

- **Endpoint:** `/reverse_geocode`
- **Método:** `GET`
- **Parámetros:** `?lat=...&lon=...`

---

## 2. Endpoints para Conductores (App Delivery)

Estos endpoints son exclusivos para la aplicación de los repartidores.

### 2.1. Actualizar Ubicación (Fake GPS / Real GPS)

Envía la ubicación en tiempo real del conductor. **CRÍTICO:** La App debe llamar a este endpoint frecuentemente (ej. cada 5-10 segundos) para que el sistema de asignación por cercanía funcione correctamente.

- **Endpoint:** `/driver/location`
- **Método:** `POST`
- **Payload:**
  ```json
  {
    "driver_id": "D1",
    "latitude": -17.7833,
    "longitude": -63.1821
  }
  ```

### 2.2. Obtener Mis Pedidos (Polling)

Obtiene los pedidos asignados a un conductor específico. La App debe consultar esto periódicamente (Polling).
**IMPORTANTE:** Cada objeto de pedido incluye ahora `restaurant_location`. La App debe usar esto para trazar la ruta de recogida (Driver -> Restaurante) y luego la de entrega (Restaurante -> Cliente).

- **Endpoint:** `/driver/orders/<driver_id>`
- **Método:** `GET`
- **Respuesta:** Lista de objetos `order`.
  ```json
  [
      {
          "id": "ORD-123",
          "status": "Repartidor Asignado",
          "items": [...],
          "total": 150.00,
          "location": { "latitude": -17.555, "longitude": -63.555 }, // Ubicación Cliente
          "restaurant_location": {                                    // Ubicación Restaurante (Recogida)
              "latitude": -17.7832662,
              "longitude": -63.1820985,
              "name": "Pizzería Nova"
          }
      }
  ]
  ```
  - _Nota:_ Si el pedido fue asignado a otro conductor (por estar más cerca), este endpoint devolverá una lista vacía (o sin ese pedido) para el conductor lejano.

### 2.3. Aceptar Pedido

El conductor confirma que realizará la entrega. **Incluye validación de seguridad.**

- **Endpoint:** `/driver/accept`
- **Método:** `POST`
- **Payload:** `{"order_id": "ORD-123", "driver_id": "D1"}`
- **Respuestas:**
  - `200 OK`: Aceptado correctamente.
  - `409 Conflict`: "Este pedido ya fue aceptado por otro conductor." (Si el conductor intenta aceptar un pedido que el sistema asignó a otro).
- **Efecto:** Cambia estado a `Repartidor Asignado` y notifica al cliente.

### 2.4. Recoger Pedido

El conductor recoge el pedido del restaurante.

- **Endpoint:** `/driver/pickup`
- **Método:** `POST`
- **Payload:** `{"order_id": "ORD-123"}`
- **Efecto:** Cambia estado a `En camino` y notifica al cliente.

### 2.5. Entregar Pedido

El conductor entrega el pedido al cliente.

- **Endpoint:** `/driver/deliver`
- **Método:** `POST`
- **Payload:** `{"order_id": "ORD-123"}`
- **Efecto:**
  1. Cambia estado a `Entregado`.
  2. Notifica al cliente vía Telegram.
  3. **Incluye un botón "⭐ Calificar Pedido"** en el mensaje de Telegram.
     - Este botón abre la WebApp con parámetros: `?order_id=ORD-123&action=rate`.
     - **Frontend:** Debe detectar `action=rate` en la URL al iniciar y redirigir al usuario a la pantalla de "Mis Pedidos" -> "Seguimiento" -> Modal de Calificación.

---

## 3. Endpoints Administrativos (Gestión de Pedidos)

### 3.1. Actualizar Estado del Pedido (Manual/Admin)

Cambia el estado de un pedido y notifica al cliente.

- **Endpoint:** `/update_status/<order_id>`
- **Método:** `POST`
- **Payload:** `{"status": "Nuevo Estado"}`

### 3.2. Obtener Todos los Pedidos

- **Endpoint:** `/get_orders`
- **Método:** `GET`

### 3.3. Rastrear Pedido Individual (Polling)

Para mostrar el estado en tiempo real en el Frontend.

- **Endpoint:** `/get_order/<order_id>`
- **Método:** `GET`
- **Respuesta:** Incluye `status`, `driver_location` y **`restaurant_location`**.
  ```json
  {
    "id": "ORD-123",
    "status": "En camino",
    "driver_location": {
      "latitude": -17.7835,
      "longitude": -63.1822
    },
    "restaurant_location": {
      "latitude": -17.7832662,
      "longitude": -63.1820985,
      "name": "Plaza 24 de Septiembre"
    },
    "restaurant_map_location": {
      "latitude": -17.7836162,
      "longitude": -63.1814985
    }
  }
  ```
  > [!IMPORTANT] > **Ubicación del Restaurante:** El Frontend debe usar `restaurant_location` (o `restaurant_map_location` para evitar superposición en el mapa) que viene en esta respuesta como la **Fuente de Verdad** para pintar el marcador del restaurante, en lugar de tener coordenadas harcodeadas.

---

## 4. Flujo de Notificaciones (Automático)

1.  **Confirmación:** "✅ ¡Tu pedido ha sido confirmado!"
2.  **Repartidor Asignado:** "🛵 ¡Un repartidor ha aceptado tu pedido!"
3.  **En Camino:** "🚀 ¡Tu pedido ya está en camino!"
4.  **Entregado:** "🎉 ¡Tu pedido ha sido entregado!"

El backend actúa como orquestador entre la WebApp, la App de Delivery y el Chat de Telegram.

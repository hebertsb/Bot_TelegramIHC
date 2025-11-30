# Respuesta al Equipo Frontend

Hola equipo, aquí están las confirmaciones técnicas para la integración:

## 1. Endpoint `/get_order/<order_id>`

*   **Formato de Respuesta:** Confirmado. La respuesta JSON **siempre** incluirá:
    *   `restaurant_location`: `{ "latitude": float, "longitude": float, "name": string }` (Fuente de verdad).
    *   `restaurant_map_location`: `{ "latitude": float, "longitude": float }` (Coordenadas desplazadas para el pin del mapa).
    *   `driver_location`: `{ "latitude": float, "longitude": float }` o `null` (si no hay conductor activo/asignado).

*   **Fallback:** `restaurant_map_location` siempre se envía desde el backend (está en `config.py`), por lo que no debería faltar. Sin embargo, usar `restaurant_location` como fallback es una buena práctica defensiva.
*   **Nombre del Restaurante:** Sí, viene en `restaurant_location.name`.

**Ejemplo JSON Completo:**
```json
{
    "id": "ORD-1716234567",
    "status": "En camino",
    "total": 150.50,
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
    },
    "items": [...],
    "customer_name": "Juan Perez"
}
```

## 2. Endpoint `POST /submit_order`

*   **Generación de ID (`order.id`):**
    *   **Preferible:** Que el **Frontend** genere el ID (ej. `ORD-{timestamp}-{random}`).
    *   **Backend:** Si el frontend NO lo envía, el backend lo generará automáticamente, pero recomendamos que lo generen ustedes para tener la referencia inmediata en la UI.
*   **Campos Requeridos:** Confirmamos la lista.
    *   `id`, `items[]`, `total`, `address`, `location` (lat/lng), `paymentMethod`, `date`, `status` ("Pendiente"), `customer_name`, `customer_phone`.
    *   `customer_nit` es opcional (se usa para la factura).
*   **Validaciones:** No hay límites estrictos de longitud ("hard limits") en el backend para teléfono o NIT por ahora, pero se recomienda validar en frontend formatos lógicos.

## 3. CORS y Polling

*   **CORS:** El backend está configurado para aceptar peticiones (normalmente `CORS(app)` permite `*` en este entorno de desarrollo/pruebas). Si tienen problemas de bloqueo, avísennos para revisar la whitelist.
*   **Polling:** Un intervalo de **5 segundos** es perfecto y recomendado para mantener la ubicación del conductor actualizada sin saturar el servidor.

## 4. Estados y Notificaciones

*   **Estados del Sistema (Exactos):**
    1.  `Pendiente` (Al crear el pedido)
    2.  `Confirmado` (Restaurante acepta)
    3.  `En preparación` (Cocina)
    4.  `Repartidor Asignado` (Conductor acepta)
    5.  `En camino` (Conductor recoge y sale)
    6.  `Entregado` (Fin del flujo)
    7.  `Cancelado`

*   **Actualización `driver_location`:** Sí, es tiempo real. La App de Delivery envía actualizaciones cada pocos segundos al backend, y este las guarda en el pedido. Su polling a `/get_order` reflejará estos cambios.

## 5. Otros

*   **Superposición en Mapa:** Confirmado. `restaurant_map_location` tiene un pequeño desplazamiento (offset) intencional respecto a la ubicación real para que, si la moto está parada en el restaurante, se vean ambos iconos (Moto y Tienda) y no uno encima del otro. **Usen `restaurant_map_location` para el pin del mapa.**
*   **Datos del Conductor:** Por ahora el sistema maneja `driver_id`. No estamos exponiendo `driver_name` o `driver_phone` en el objeto `order` de respuesta pública por privacidad/simplicidad en esta fase, pero el `driver_id` sirve para debug.

---
**Resumen para Frontend:**
Implementen el polling a `/get_order`, usen las coordenadas de restaurante provistas en el JSON y respeten el flujo de estados mencionado. ¡Gracias!

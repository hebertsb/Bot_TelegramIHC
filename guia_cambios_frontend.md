# 📋 Guía de Implementación Frontend (Actualización Ubicación y Tracking)

Esta guía detalla los cambios necesarios en el Frontend (React/WebApp) para integrarse con la nueva lógica centralizada del Backend.

## 🚨 Cambios Críticos

### 1. Eliminar Simulación Local
El Backend ya **NO** simula el movimiento del conductor ni los cambios de estado automáticamente.
*   **Acción:** Elimina o comenta cualquier función tipo `startDeliveryAnimation` o `simulateDriverMovement` en tu código.
*   **Nueva Lógica:** La UI debe ser puramente reactiva a lo que devuelve el endpoint `/get_order`. Si el estado es "En camino", muestra el mapa; si cambia a "Entregado", muestra la confirmación.

### 2. Ubicación del Restaurante (Fuente de Verdad)
Ya no debes tener las coordenadas del restaurante "quemadas" (hardcoded) en el código del Frontend. Ahora vienen del servidor.

*   **Endpoint:** `GET /get_order/<order_id>`
*   **Campos a usar:**
    *   `restaurant_location`: Coordenadas exactas del local.
    *   `restaurant_map_location`: Coordenadas ligeramente desplazadas (usar estas para el **marcador del mapa** para evitar que se superponga con el conductor si están muy cerca).

#### Ejemplo de Respuesta API:
```json
{
    "id": "ORD-123",
    "status": "En camino",
    "driver_location": { "latitude": -17.7835, "longitude": -63.1822 },
    "restaurant_location": { ... },
    "restaurant_map_location": { 
        "latitude": -17.7836162, 
        "longitude": -63.1814985 
    } 
}
```

### 3. Tracking en Tiempo Real
El movimiento del conductor ahora es real y depende de la App de Delivery.

*   **Acción:** Tu componente de Mapa debe hacer **Polling** (consultar cada 5-10 segundos) al endpoint `/get_order/<order_id>`.
*   **Actualización:**
    *   Si `driver_location` no es null, actualiza la posición del marcador de la moto 🛵.
    *   Si `driver_location` es null, mantén la moto en `restaurant_map_location` (esperando salir).

## 💡 Snippet de Ejemplo (React)

```javascript
// Ejemplo conceptual de cómo manejar los datos del backend

const [order, setOrder] = useState(null);

useEffect(() => {
  const fetchOrder = async () => {
    const response = await fetch(`https://.../get_order/${orderId}`);
    const data = await response.json();
    setOrder(data);
  };

  // Polling cada 5 segundos
  const interval = setInterval(fetchOrder, 5000);
  return () => clearInterval(interval);
}, [orderId]);

// En tu render del Mapa:
const restaurantPos = order?.restaurant_map_location || DEFAULT_COORDS; // Fallback solo por seguridad
const driverPos = order?.driver_location || restaurantPos;

return (
  <Map>
     <Marker position={restaurantPos} icon="🏪" />
     {order?.status === "En camino" && (
        <Marker position={driverPos} icon="🛵" />
     )}
  </Map>
);
```

## ✅ Checklist para el Desarrollador Frontend
- [ ] Eliminar lógica de simulación de tiempos y estados.
- [ ] Consumir `restaurant_map_location` del endpoint `/get_order`.
- [ ] Implementar polling para actualizar la posición del conductor desde `driver_location`.
- [ ] Verificar que los estados ("Confirmado", "En camino", "Entregado") se actualicen solos según la respuesta del API.

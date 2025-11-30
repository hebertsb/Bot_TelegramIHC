# 🔄 Flujo de Estados y UI del Frontend

Este documento explica cómo el Frontend debe reaccionar a los cambios de estado del Backend para ofrecer la experiencia de tracking en tiempo real.

## 🧠 Concepto Clave: El Frontend es un "Espectador"
El Frontend **NO** cambia el estado del pedido (no decide cuándo sale la moto ni cuándo llega).
*   **Quién cambia el estado:** El Restaurante (acepta/cocina) y el Repartidor (recoge/entrega).
*   **Qué hace el Frontend:** Consulta constantemente (`Polling`) al servidor para "ver qué está pasando" y actualiza la pantalla.

---

## 📍 Máquina de Estados de la UI

El Frontend debe tener un `switch` o lógica condicional basada en `order.status` que viene de `/get_order`.

### 1. Estado: `Pendiente` / `Confirmado`
*   **Qué significa:** El pedido se creó y el restaurante lo aceptó.
*   **UI a mostrar:**
    *   ✅ Stepper o Barra de Progreso: Paso 1 activo.
    *   ❌ **Mapa:** OCULTO (o estático mostrando solo el restaurante).
    *   ℹ️ **Texto:** "Esperando confirmación..." o "El restaurante ha aceptado tu pedido".

### 2. Estado: `En preparación`
*   **Qué significa:** Están cocinando.
*   **UI a mostrar:**
    *   ✅ Stepper: Paso 2 activo.
    *   ❌ **Mapa:** OCULTO.
    *   👨‍🍳 **Animación:** Icono de cocinero o pizza en horno.

### 3. Estado: `Repartidor Asignado`
*   **Qué significa:** Un conductor aceptó el pedido y está yendo al restaurante.
*   **UI a mostrar:**
    *   ✅ Stepper: Paso 3 activo ("Conductor asignado").
    *   ⚠️ **Mapa:** OPCIONAL. Podrías mostrar al conductor yendo al restaurante, pero lo estándar es esperar a que recoja el pedido.
    *   🛵 **Info:** "Tu repartidor está en camino al local".

### 4. Estado: `En camino` (🔥 EL MOMENTO CLAVE)
*   **Qué significa:** El conductor ya recogió la pizza y está yendo hacia el cliente.
*   **UI a mostrar:**
    *   ✅ Stepper: Paso 4 activo ("En camino").
    *   🗺️ **Mapa:** **VISIBLE Y ACTIVO**.
    *   **Lógica del Mapa:**
        1.  Leer `restaurant_map_location` -> Pintar Pin 🏪 (Fijo).
        2.  Leer `order.location` -> Pintar Pin 🏠 (Fijo, casa del cliente).
        3.  Leer `driver_location` -> Pintar Pin 🛵 (**MÓVIL**).
        4.  **Actualización:** Cada 5 segundos (en el siguiente polling), `driver_location` cambiará. Mueve el Pin 🛵 suavemente a la nueva posición.

### 5. Estado: `Entregado`
*   **Qué significa:** El conductor marcó "Entregado" en su App.
*   **UI a mostrar:**
    *   ✅ Stepper: Paso 5 completado.
    *   ❌ **Mapa:** OCULTO (ya no es necesario).
    *   🎉 **Pantalla:** "¡Disfruta tu pedido!".
    *   ⭐ **Acción:** Abrir automáticamente el **Modal de Calificación**.

---

## 📝 Resumen del Loop Técnico (Polling)

1.  **Inicio:** El usuario hace Checkout.
2.  **Loop (cada 5s):** Frontend llama a `GET /get_order/<id>`.
3.  **Recibe JSON:**
    ```json
    {
        "status": "En camino",
        "driver_location": { "lat": -17.88, "lon": -63.55 },
        ...
    }
    ```
4.  **Reacción:**
    *   ¿Estado cambió a `En camino`? -> **Montar componente Mapa**.
    *   ¿Estado sigue `En camino`? -> **Actualizar coordenadas del Pin Moto**.
    *   ¿Estado cambió a `Entregado`? -> **Desmontar Mapa** y **Mostrar Modal Rating**.

## ⭐ Sobre la Calificación
Actualmente el backend recibe `isRated` en el objeto del pedido, pero no tenemos un endpoint específico `/rate_order` documentado hoy.
*   **Por ahora:** El Frontend puede guardar la calificación localmente o simplemente mostrar el agradecimiento.
*   **Futuro:** Crearemos un endpoint `POST /rate_order` para guardar las estrellas y comentarios.

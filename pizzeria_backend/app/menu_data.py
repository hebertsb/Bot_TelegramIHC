# pizzeria_backend/app/menu_data.py

# Este archivo centraliza los datos del menú.
# En un futuro, esto podría ser reemplazado por una llamada a una base de datos.

products = {
    "promociones": [
        {
            "id": "promo-1",
            "name": "Combo Amigos",
            "description": "2 Pizzas Grandes (cualquier sabor) + 1 Gaseosa 2L.",
            "price": 120.50,
            "image": "https://i.imgur.com/example.jpg"
        },
        {
            "id": "promo-2",
            "name": "Promo Personal",
            "description": "1 Pizza Mediana + 1 Gaseosa Personal.",
            "price": 65.00,
            "image": "https://i.imgur.com/example2.jpg"
        }
    ],
    "pizzas": [
        {
            "id": "pizza-1",
            "name": "Margarita",
            "description": "Clásica pizza con salsa de tomate, mozzarella y albahaca.",
            "price": 55.00,
            "image": "https://i.imgur.com/pizzamarga.jpg"
        },
        {
            "id": "pizza-2",
            "name": "Pepperoni",
            "description": "La favorita de todos, con abundante pepperoni y queso.",
            "price": 65.00,
            "image": "https://i.imgur.com/pizzapepp.jpg"
        },
        {
            "id": "pizza-3",
            "name": "Hawaiana",
            "description": "La controversial pero deliciosa pizza con piña y jamón.",
            "price": 68.00,
            "image": "https://i.imgur.com/pizzahawai.jpg"
        }
    ],
    "adicionales": [
        {
            "id": "adic-1",
            "name": "Extra Queso",
            "price": 10.00
        },
        {
            "id": "adic-2",
            "name": "Borde Relleno de Queso",
            "price": 15.00
        }
    ],
    "bebidas": [
        {
            "id": "beb-1",
            "name": "Gaseosa 2L",
            "price": 15.00
        },
        {
            "id": "beb-2",
            "name": "Agua 1L",
            "price": 8.00
        }
    ]
}

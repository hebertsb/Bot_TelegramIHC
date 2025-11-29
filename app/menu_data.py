# pizzeria_backend/app/menu_data.py

# Este archivo centraliza los datos del menú del restaurante.
# Organizado en categorías: promociones, pizzas, bebidas, postres y adicionales.

products = {
    "promociones": [
        {
            "id": "promo-1",
            "name": "Combo Pizza + Coca-Cola",
            "description": "Pizza mediana de tu elección + Coca-Cola 500ml. ¡Perfecto para una comida rápida!",
            "price": 76.00,
            "emoji": "🔥",
            "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=500&h=350&fit=crop"
        },
        {
            "id": "promo-2",
            "name": "Promo Familiar (2 Pizzas + 2 Bebidas)",
            "description": "2 Pizzas grandes + 2 Bebidas de 500ml. Ideal para compartir en familia.",
            "price": 124.00,
            "emoji": "👨‍👩‍👧‍👦",
            "image": "https://images.unsplash.com/photo-1571997478779-2adcbbe9ab2f?w=500&h=350&fit=crop"
        },
        {
            "id": "promo-3",
            "name": "Combo Pareja (Pizza Mediana + Postre)",
            "description": "Pizza mediana + Postre a elección. Perfecto para una cita romántica.",
            "price": 100.00,
            "emoji": "💞",
            "image": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=500&h=350&fit=crop"
        },
        {
            "id": "promo-4",
            "name": "Combo Fiesta (3 Pizzas + 1.5L Gaseosa)",
            "description": "3 Pizzas grandes + Gaseosa 1.5L. ¡Para celebrar con amigos!",
            "price": 186.00,
            "emoji": "🎉",
            "image": "https://images.unsplash.com/photo-1534308983496-4fabb1a015ee?w=500&h=350&fit=crop"
        },
        {
            "id": "promo-5",
            "name": "Almuerzo Express (Pizza Personal + Bebida)",
            "description": "Pizza personal + Bebida. Rápido y delicioso para tu almuerzo.",
            "price": 59.00,
            "emoji": "⏱️",
            "image": "https://images.unsplash.com/photo-1595854341625-f33ee10dbf94?w=500&h=350&fit=crop"
        },
        {
            "id": "promo-6",
            "name": "Noche Italiana (Pizza Gourmet + Vino)",
            "description": "Pizza gourmet de tu elección + Copa de vino tinto. Una experiencia premium.",
            "price": 152.00,
            "emoji": "🍷",
            "image": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=500&h=350&fit=crop"
        }
    ],
    "pizzas": [
        {
            "id": "pizza-1",
            "name": "Pizza Pepperoni",
            "description": "La clásica favorita con rodajas de pepperoni y queso mozzarella derretido.",
            "price": 69.00,
            "emoji": "🍕",
            "image": "https://images.unsplash.com/photo-1628840042765-356cda07504e?w=500&h=350&fit=crop"
        },
        {
            "id": "pizza-2",
            "name": "Pizza Hawaiana",
            "description": "La combinación perfecta de jamón, piña dulce y queso. ¡Controversial pero deliciosa!",
            "price": 83.00,
            "emoji": "🍍",
            "image": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=500&h=350&fit=crop"
        },
        {
            "id": "pizza-3",
            "name": "Pizza Margarita",
            "description": "Clásica italiana con salsa de tomate fresco, mozzarella y albahaca.",
            "price": 62.00,
            "emoji": "🌿",
            "image": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=500&h=350&fit=crop"
        },
        {
            "id": "pizza-4",
            "name": "Pizza Cuatro Quesos",
            "description": "Mezcla exquisita de mozzarella, parmesano, gorgonzola y provolone.",
            "price": 79.00,
            "emoji": "🧀",
            "image": "https://images.unsplash.com/photo-1571997478779-2adcbbe9ab2f?w=500&h=350&fit=crop"
        },
        {
            "id": "pizza-5",
            "name": "Pizza Vegetariana",
            "description": "Cargada de vegetales frescos: pimientos, champiñones, cebolla, aceitunas y tomate.",
            "price": 72.00,
            "emoji": "🥦",
            "image": "https://images.unsplash.com/photo-1511689660979-10d2b1aada49?w=500&h=350&fit=crop"
        },
        {
            "id": "pizza-6",
            "name": "Pizza BBQ Pollo",
            "description": "Pollo marinado en salsa BBQ, cebolla morada, cilantro y queso mozzarella.",
            "price": 86.00,
            "emoji": "🍗",
            "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=500&h=350&fit=crop"
        },
        {
            "id": "pizza-7",
            "name": "Pizza Napolitana",
            "description": "Tomates frescos, ajo, orégano, aceitunas negras y anchoas sobre mozzarella.",
            "price": 76.00,
            "emoji": "🍅",
            "image": "https://images.unsplash.com/photo-1595708684082-a173bb3a06c5?w=500&h=350&fit=crop"
        },
        {
            "id": "pizza-8",
            "name": "Pizza Mexicana",
            "description": "Picante y sabrosa con jalapeños, carne molida, frijoles, pimientos y queso cheddar.",
            "price": 90.00,
            "emoji": "🌶️",
            "image": "https://images.unsplash.com/photo-1534308983496-4fabb1a015ee?w=500&h=350&fit=crop"
        },
        {
            "id": "pizza-9",
            "name": "Pizza Mar y Tierra",
            "description": "Combinación gourmet de camarones, carne de res, pimientos y cebolla.",
            "price": 97.00,
            "emoji": "🦐",
            "image": "https://images.unsplash.com/photo-1593560708920-61dd98c46a4e?w=500&h=350&fit=crop"
        },
        {
            "id": "pizza-10",
            "name": "Pizza Caprese",
            "description": "Tomates cherry, mozzarella fresca, albahaca y un toque de aceite de oliva.",
            "price": 76.00,
            "emoji": "🍃",
            "image": "https://images.unsplash.com/photo-1571407970349-bc81e7e96c47?w=500&h=350&fit=crop"
        },
        {
            "id": "pizza-11",
            "name": "Pizza de Jamón y Champiñones",
            "description": "Jamón premium, champiñones frescos y queso mozzarella sobre salsa de tomate.",
            "price": 83.00,
            "emoji": "🍄",
            "image": "https://images.unsplash.com/photo-1565299507177-b0ac66763828?w=500&h=350&fit=crop"
        }
    ],
    "bebidas": [
        {
            "id": "beb-1",
            "name": "Coca-Cola (500ml)",
            "description": "La bebida refrescante clásica.",
            "price": 14.00,
            "emoji": "🥤",
            "image": "https://images.unsplash.com/photo-1554866585-cd94860890b7?w=500&h=350&fit=crop"
        },
        {
            "id": "beb-2",
            "name": "Agua Mineral (500ml)",
            "description": "Agua purificada y refrescante.",
            "price": 10.00,
            "emoji": "💧",
            "image": "https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=500&h=350&fit=crop"
        },
        {
            "id": "beb-3",
            "name": "Fanta Naranja",
            "description": "Refresco de naranja burbujeante y dulce.",
            "price": 14.00,
            "emoji": "🍊",
            "image": "https://images.unsplash.com/photo-1624517452488-04869289c4ca?w=500&h=350&fit=crop"
        },
        {
            "id": "beb-4",
            "name": "Sprite",
            "description": "Refresco de lima-limón cristalino y refrescante.",
            "price": 14.00,
            "emoji": "🍋",
            "image": "https://images.unsplash.com/photo-1625772299848-391b6a87d7b3?w=500&h=350&fit=crop"
        },
        {
            "id": "beb-5",
            "name": "Cerveza Artesanal",
            "description": "Cerveza local de alta calidad con sabor único.",
            "price": 24.00,
            "emoji": "🍺",
            "image": "https://images.unsplash.com/photo-1535958636474-b021ee887b13?w=500&h=350&fit=crop"
        },
        {
            "id": "beb-6",
            "name": "Vino Tinto (Copa)",
            "description": "Copa de vino tinto de la casa, ideal para acompañar tu pizza.",
            "price": 28.00,
            "emoji": "🍷",
            "image": "https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=500&h=350&fit=crop"
        },
        {
            "id": "beb-7",
            "name": "Jugo Natural de Piña",
            "description": "Jugo fresco de piña 100% natural sin azúcar añadida.",
            "price": 17.00,
            "emoji": "🍍",
            "image": "https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=500&h=350&fit=crop"
        },
        {
            "id": "beb-8",
            "name": "Limonada con Hierbabuena",
            "description": "Refrescante limonada casera con hojas de hierbabuena fresca.",
            "price": 17.00,
            "emoji": "🍋",
            "image": "https://images.unsplash.com/photo-1523677011781-c91d1bbe2f0d?w=500&h=350&fit=crop"
        }
    ],
    "postres": [
        {
            "id": "post-1",
            "name": "Tarta de Chocolate",
            "description": "Deliciosa tarta de chocolate con cobertura de ganache.",
            "price": 35.00,
            "emoji": "🍰",
            "image": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=500&h=350&fit=crop"
        },
        {
            "id": "post-2",
            "name": "Helado de Vainilla",
            "description": "Cremoso helado artesanal de vainilla.",
            "price": 21.00,
            "emoji": "🍨",
            "image": "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=500&h=350&fit=crop"
        },
        {
            "id": "post-3",
            "name": "Cheesecake de Fresa",
            "description": "Suave cheesecake con coulis de fresas frescas.",
            "price": 31.00,
            "emoji": "🍓",
            "image": "https://images.unsplash.com/photo-1533134242443-d4fd215305ad?w=500&h=350&fit=crop"
        },
        {
            "id": "post-4",
            "name": "Tiramisú",
            "description": "El clásico postre italiano con café, mascarpone y cacao.",
            "price": 38.00,
            "emoji": "☕",
            "image": "https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=500&h=350&fit=crop"
        },
        {
            "id": "post-5",
            "name": "Brownie con Helado",
            "description": "Brownie de chocolate caliente con bola de helado de vainilla.",
            "price": 41.00,
            "emoji": "🍫",
            "image": "https://images.unsplash.com/photo-1607920591413-4ec007e70023?w=500&h=350&fit=crop"
        },
        {
            "id": "post-6",
            "name": "Pan de Ajo Dulce",
            "description": "Pan de ajo con un toque dulce, perfecto para compartir.",
            "price": 24.00,
            "emoji": "🥖",
            "image": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=500&h=350&fit=crop"
        },
        {
            "id": "post-7",
            "name": "Mini Cannoli",
            "description": "Tradicionales cannoli sicilianos rellenos de ricotta dulce.",
            "price": 28.00,
            "emoji": "🥐",
            "image": "https://images.unsplash.com/photo-1519915212116-7cfef71f1d3e?w=500&h=350&fit=crop"
        }
    ],
    "adicionales": [
        {
            "id": "adic-1",
            "name": "Extra Queso Mozzarella",
            "description": "Porción adicional de queso mozzarella para tu pizza.",
            "price": 10.00,
            "emoji": "🧀"
        },
        {
            "id": "adic-2",
            "name": "Borde Relleno de Queso",
            "description": "Transforma tu pizza con un delicioso borde relleno de queso.",
            "price": 15.00,
            "emoji": "🥖"
        },
        {
            "id": "adic-3",
            "name": "Extra Pepperoni",
            "description": "Más rodajas de pepperoni para los amantes de este ingrediente.",
            "price": 12.00,
            "emoji": "🍕"
        },
        {
            "id": "adic-4",
            "name": "Extra Champiñones",
            "description": "Champiñones frescos adicionales.",
            "price": 8.00,
            "emoji": "🍄"
        },
        {
            "id": "adic-5",
            "name": "Extra Jamón",
            "description": "Porción adicional de jamón premium.",
            "price": 10.00,
            "emoji": "🥓"
        },
        {
            "id": "adic-6",
            "name": "Extra Aceitunas",
            "description": "Aceitunas negras adicionales.",
            "price": 6.00,
            "emoji": "🫒"
        },
        {
            "id": "adic-7",
            "name": "Extra Piña",
            "description": "Más piña dulce para tu pizza hawaiana.",
            "price": 7.00,
            "emoji": "🍍"
        },
        {
            "id": "adic-8",
            "name": "Salsa Picante Extra",
            "description": "Porción de salsa picante casera para acompañar.",
            "price": 3.00,
            "emoji": "🌶️"
        },
        {
            "id": "adic-9",
            "name": "Salsa Ranch",
            "description": "Deliciosa salsa ranch para mojar tu pizza.",
            "price": 5.00,
            "emoji": "🥛"
        },
        {
            "id": "adic-10",
            "name": "Pan de Ajo (6 piezas)",
            "description": "Pan de ajo tostado con mantequilla y hierbas.",
            "price": 18.00,
            "emoji": "🥖"
        }
    ]
}


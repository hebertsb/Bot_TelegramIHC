import logging
import firebase_admin
from firebase_admin import credentials, firestore
from config import FIREBASE_CREDENTIALS

# --- Configuración del Logging ---
logger = logging.getLogger(__name__)

def _initialize_firebase():
    """
    Inicializa la conexión con Firebase de forma segura y devuelve el cliente de DB.
    Esta es una función interna para ser llamada solo una vez.
    """
    try:
        # logger.info(f"Intentando inicializar Firebase...") # Evitar loguear credenciales si es un dict
        cred = credentials.Certificate(FIREBASE_CREDENTIALS)
        firebase_admin.initialize_app(cred)
        db_client = firestore.client()
        logger.info("¡Conexión con Firebase establecida exitosamente!")
        return db_client
    except Exception as e:
        logger.error(f"CRÍTICO: La conexión con Firebase falló en el inicio. Error: {e}", exc_info=True)
        return None

# --- Variable Global para Firebase ---
# Se inicializa una sola vez cuando el módulo es importado.
db = _initialize_firebase()

def guardar_pedido_en_firestore(order_data):
    """
    Guarda un nuevo pedido en la colección 'pedidos' de Firestore.
    Verifica si la conexión a la base de datos está disponible.
    """
    if not db:
        logger.error("No se puede guardar el pedido: La conexión con Firebase no está disponible o falló en el inicio.")
        return False
    
    order_id = None  # Inicializar order_id
    try:
        order_id = str(order_data.get("id", "unknown_id"))
        if order_id == "unknown_id":
            logger.warning("El pedido no tiene un 'id' válido.")
            return False
            
        db.collection('pedidos').document(order_id).set(order_data)
        logger.info(f"Pedido {order_id} guardado exitosamente en Firestore.")
        return True
    except Exception as e:
        # Ahora order_id siempre existirá, incluso si es None
        logger.error(f"Error al intentar guardar el pedido {order_id or 'desconocido'} en Firestore: {e}", exc_info=True)
        return False

def obtener_pedido_por_id(order_id):
    """
    Obtiene un pedido específico de Firestore por su ID.
    """
    if not db:
        logger.error("No se puede obtener el pedido: La conexión con Firebase no está disponible.")
        return None
        
    try:
        logger.info(f"Buscando pedido con ID: {order_id}")
        doc_ref = db.collection('pedidos').document(str(order_id))
        doc = doc_ref.get()
        if doc.exists:
            logger.info(f"Pedido {order_id} encontrado.")
            return doc.to_dict()
        else:
            logger.warning(f"No se encontró ningún pedido con el ID: {order_id}")
            return None
    except Exception as e:
        logger.error(f"Error al obtener el pedido {order_id} de Firestore: {e}", exc_info=True)
        return None

def actualizar_estado_pedido(order_id, nuevo_estado):
    """
    Actualiza el estado de un pedido en Firestore.
    """
    if not db:
        logger.error("No se puede actualizar el estado: La conexión con Firebase no está disponible.")
        return False
    
    try:
        logger.info(f"Actualizando estado del pedido {order_id} a '{nuevo_estado}'")
        doc_ref = db.collection('pedidos').document(str(order_id))
        
        # Usamos update para modificar solo el campo 'status'
        doc_ref.update({'status': nuevo_estado})
        
        logger.info(f"Estado del pedido {order_id} actualizado exitosamente.")
        return True
    except Exception as e:
        logger.error(f"Error al actualizar el estado del pedido {order_id}: {e}", exc_info=True)
        return False

def obtener_todos_los_pedidos():
    """
    Obtiene todos los pedidos de la colección 'pedidos' en Firestore,
    ordenados por fecha descendente.
    """
    if not db:
        logger.error("No se pueden obtener los pedidos: La conexión con Firebase no está disponible.")
        return []
        
    try:
        logger.info("Obteniendo todos los pedidos de Firestore...")
        # Se ordena por 'date' en orden descendente para obtener los más recientes primero.
        pedidos_ref = db.collection('pedidos').order_by('date', direction=firestore.Query.DESCENDING).stream()
        
        pedidos = [doc.to_dict() for doc in pedidos_ref]
        
        logger.info(f"Se encontraron {len(pedidos)} pedidos.")
        return pedidos
    except Exception as e:
        logger.error(f"Error al obtener todos los pedidos de Firestore: {e}", exc_info=True)
        # Si hay un error (ej. el campo 'date' no existe en todos los docs), intenta sin ordenar.
        try:
            logger.warning("Intentando obtener pedidos sin ordenar por fecha.")
            pedidos_ref = db.collection('pedidos').stream()
            pedidos = [doc.to_dict() for doc in pedidos_ref]
            logger.info(f"Se encontraron {len(pedidos)} pedidos sin ordenar.")
            return pedidos
        except Exception as e_inner:
            logger.error(f"Error crítico al obtener todos los pedidos (segundo intento): {e_inner}", exc_info=True)
            return []
# app/routes/transactions.py
from flask import Blueprint, jsonify, request
from app.database import supabase
import requests
import logging

logger = logging.getLogger(__name__)
transactions_bp = Blueprint("transactions", __name__)

@transactions_bp.route("/transactions", methods=["POST"])
def nueva_transaccion():
    """
    Recibe una transacción (título académico pendiente), la guarda localmente
    y la propaga a todos los nodos registrados en la red.
    
    Body JSON esperado:
    {
        "persona_id": "uuid",
        "institucion_id": "uuid",
        "programa_id": "uuid",
        "titulo_obtenido": "Ingeniero en Sistemas",
        "fecha_fin": "2024-06-01",
        ...
    }
    """
    datos = request.get_json()
    
    # Validar campos mínimos requeridos
    campos_requeridos = ["persona_id", "institucion_id", "titulo_obtenido", "fecha_fin"]
    for campo in campos_requeridos:
        if campo not in datos:
            return jsonify({"error": f"Campo requerido faltante: {campo}"}), 400
    
    try:
        # 1. Guardar localmente en transacciones_pendientes
        response = supabase.table("transacciones_pendientes").insert(datos).execute()
        logger.info(f"💾 Transacción guardada localmente: {datos.get('titulo_obtenido')}")
        
        # 2. Propagar a los demás nodos registrados
        _propagar_transaccion(datos)
        
        return jsonify({
            "mensaje": "✅ Transacción creada y propagada",
            "transaccion": response.data[0] if response.data else datos
        }), 201
    
    except Exception as e:
        logger.error(f"❌ Error al crear transacción: {str(e)}")
        return jsonify({"error": str(e)}), 500

def _propagar_transaccion(datos: dict):
    """
    Envía la transacción a todos los nodos registrados.
    Si un nodo falla, solo se loggea el error (la red sigue funcionando).
    """
    try:
        nodos = supabase.table("nodos").select("url").execute().data or []
        
        for nodo in nodos:
            url_nodo = nodo["url"]
            try:
                resp = requests.post(
                    f"{url_nodo}/transactions",
                    json=datos,
                    timeout=3  # No esperar más de 3 segundos por nodo
                )
                logger.info(f"📡 Propagado a {url_nodo}: {resp.status_code}")
            except requests.exceptions.RequestException as e:
                # Si el nodo está caído, la red sigue funcionando
                logger.warning(f"⚠  Nodo {url_nodo} no disponible: {str(e)}")
    
    except Exception as e:
        logger.error(f"❌ Error durante propagación: {str(e)}")
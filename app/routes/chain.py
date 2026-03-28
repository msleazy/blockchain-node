# app/routes/chain.py
from flask import Blueprint, jsonify
from app.database import supabase
import logging

logger = logging.getLogger(__name__)
chain_bp = Blueprint("chain", __name__)

@chain_bp.route("/chain", methods=["GET"])
def obtener_cadena():
    """
    Retorna todos los bloques minados de este nodo, ordenados cronológicamente.
    Otros nodos usan este endpoint para comparar cadenas en el consenso.
    """
    try:
        # Obtenemos todos los grados (bloques) ordenados por fecha de creación
        response = supabase.table("grados") \
            .select("*") \
            .order("creado_en", desc=False) \
            .execute()
        
        cadena = response.data or []
        logger.info(f"📦 Cadena solicitada: {len(cadena)} bloques")
        
        return jsonify({
            "chain": cadena,
            "length": len(cadena)
        }), 200
    
    except Exception as e:
        logger.error(f"❌ Error al obtener cadena: {str(e)}")
        return jsonify({"error": str(e)}), 500

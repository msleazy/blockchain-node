# app/routes/transactions.py
from flask import Blueprint, jsonify, request
from app.database import supabase
import requests
import logging
logger = logging.getLogger(__name__)
transactions_bp = Blueprint("transactions", __name__)

@transactions_bp.route("/transactions", methods=["POST"])
def nueva_transaccion():
    datos = request.get_json()

    campos_requeridos = ["persona_id", "institucion_id", "titulo_obtenido", "fecha_fin"]
    for campo in campos_requeridos:
        if campo not in datos:
            return jsonify({"error": f"Campo requerido faltante: {campo}"}), 400

    # ✅ Leer el flag antes de insertar
    propagar = datos.pop("propagar", True)

    try:
        response = supabase.table("transacciones_pendientes").insert(datos).execute()
        logger.info(f"💾 Transacción guardada: {datos.get('titulo_obtenido')}")

        # ✅ Solo propagar si viene del cliente original, no de otro nodo
        if propagar:
            _propagar_transaccion(datos)

        return jsonify({
            "mensaje": "✅ Transacción creada y propagada",
            "transaccion": response.data[0] if response.data else datos
        }), 201

    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


def _propagar_transaccion(datos: dict):
    try:
        nodos = supabase.table("nodos").select("url").execute().data or []
        for nodo in nodos:
            url_nodo = nodo["url"]
            try:
                # ✅ Enviar con propagar=False para que el nodo receptor NO reenvíe
                resp = requests.post(
                    f"{url_nodo}/transactions",
                    json={**datos, "propagar": False},
                    timeout=3
                )
                logger.info(f"📡 Propagado a {url_nodo}: {resp.status_code}")
            except requests.exceptions.RequestException as e:
                logger.warning(f"⚠ Nodo {url_nodo} no disponible: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Error durante propagación: {str(e)}")
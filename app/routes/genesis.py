from flask import Blueprint, jsonify
from app.database import supabase
import hashlib
import logging

logger = logging.getLogger(__name__)
genesis_bp = Blueprint("genesis", __name__)

@genesis_bp.route("/genesis", methods=["POST"])
def crear_genesis():
    cadena = supabase.table("grados").select("id").execute().data
    if cadena:
        return jsonify({"error": "La cadena ya tiene bloques"}), 400

    persona_id = "00000000-0000-0000-0000-000000000000"
    institucion_id = "00000000-0000-0000-0000-000000000000"
    titulo = "GENESIS"
    fecha = "2000-01-01"
    hash_anterior = ""
    nonce = 0

    while True:
        contenido = f"{persona_id}{institucion_id}{titulo}{fecha}{hash_anterior}{nonce}"
        hash_actual = hashlib.sha256(contenido.encode()).hexdigest()
        if hash_actual.startswith("000"):
            break
        nonce += 1

    bloque = {
        "titulo_obtenido": "GENESIS",
        "fecha_fin": fecha,
        "hash_actual": hash_actual,
        "hash_anterior": None,
        "nonce": nonce,
        "firmado_por": "sistema"
    }
    supabase.table("grados").insert(bloque).execute()
    logger.info(f"Bloque génesis creado: {hash_actual}")
    return jsonify({"mensaje": "Génesis creado", "bloque": bloque}), 201

# app/routes/nodes.py
from flask import Blueprint, jsonify, request
from app.database import supabase
from app.blockchain import validar_cadena
import requests
import logging

logger = logging.getLogger(__name__)
nodes_bp = Blueprint("nodes", __name__)

@nodes_bp.route("/nodes/register", methods=["POST"])
def registrar_nodo():
    """
    Registra la URL de otro nodo para que este nodo pueda comunicarse con él.
    
    Body JSON:
    { "url": "http://localhost:8002" }
    """
    datos = request.get_json()
    url = datos.get("url")
    
    if not url:
        return jsonify({"error": "Se requiere el campo 'url'"}), 400
    
    try:
        # upsert evita duplicados si el nodo ya estaba registrado
        supabase.table("nodos").upsert({"url": url}).execute()
        logger.info(f"🔗 Nodo registrado: {url}")
        
        return jsonify({
            "mensaje": f"✅ Nodo {url} registrado correctamente"
        }), 201
    
    except Exception as e:
        logger.error(f"❌ Error al registrar nodo: {str(e)}")
        return jsonify({"error": str(e)}), 500

@nodes_bp.route("/nodes", methods=["GET"])
def listar_nodos():
    """Retorna todos los nodos registrados en esta red."""
    try:
        nodos = supabase.table("nodos").select("*").execute().data or []
        return jsonify({"nodos": nodos, "total": len(nodos)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@nodes_bp.route("/nodes/resolve", methods=["GET"])
def resolver_conflictos():
    """
    Algoritmo de Consenso: Longest Chain Rule.
    
    Consulta la cadena de todos los nodos registrados.
    Si alguno tiene una cadena válida MÁS LARGA, reemplaza la cadena local.
    Esto resuelve conflictos cuando dos nodos minan al mismo tiempo.
    """
    try:
        # Cadena local actual
        cadena_local = supabase.table("grados") \
            .select("*") \
            .order("creado_en", desc=False) \
            .execute().data or []
        
        nodos = supabase.table("nodos").select("url").execute().data or []
        
        cadena_ganadora = cadena_local
        max_longitud = len(cadena_local)
        nodo_ganador = "local"
        reemplazada = False
        
        # Consultar la cadena de cada nodo registrado
        for nodo in nodos:
            url_nodo = nodo["url"]
            try:
                resp = requests.get(f"{url_nodo}/chain", timeout=5)
                
                if resp.status_code == 200:
                    data = resp.json()
                    cadena_remota = data.get("chain", [])
                    longitud_remota = data.get("lenght", 0)
                    
                    logger.info(f"🔍 Nodo {url_nodo}: {longitud_remota} bloques")
                    
                    # Regla: cadena más larga y válida gana
                    if longitud_remota > max_longitud and validar_cadena(cadena_remota):
                        cadena_ganadora = cadena_remota
                        max_longitud = longitud_remota
                        nodo_ganador = url_nodo
                        reemplazada = True
            
            except requests.exceptions.RequestException as e:
                logger.warning(f"⚠ Nodo {url_nodo} no disponible: {str(e)}")
        
        # Si encontramos una cadena más larga, reemplazamos la local
        if reemplazada:
            logger.info(f"🔄 Cadena local reemplazada con la de {nodo_ganador} ({max_longitud} bloques)")
            _reemplazar_cadena_local(cadena_ganadora)
            
            return jsonify({
                "mensaje": f"✅ Cadena reemplazada con la de {nodo_ganador}",
                "longitud_nueva": max_longitud
            }), 200
        
        logger.info("✅ Cadena local ya es la más larga. Sin cambios.")
        return jsonify({
            "mensaje": "✅ La cadena local es autoritativa",
            "longitud": max_longitud
        }), 200
    
    except Exception as e:
        logger.error(f"❌ Error en consenso: {str(e)}")
        return jsonify({"error": str(e)}), 500

def _reemplazar_cadena_local(cadena_nueva: list):
    """
    Elimina todos los bloques locales y los reemplaza con la cadena ganadora.
    CUIDADO: Solo se llama después de validar que la cadena es legítima.
    """
    # Borrar cadena actual
    supabase.table("grados").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    
    # Insertar la cadena ganadora
    for bloque in cadena_nueva:
        # Limpiar campos que Supabase auto-genera para evitar conflictos
        bloque.pop("creado_en", None)
        supabase.table("grados").upsert(bloque).execute()
    
    logger.info(f"💾 Cadena local actualizada con {len(cadena_nueva)} bloques")

# app/blockchain.py
import hashlib
import json
import logging
from datetime import datetime

# Configuración de logs (obligatorio según la rúbrica)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Dificultad del Proof of Work: el hash debe iniciar con estos ceros
DIFFICULTY = "000"

def calcular_hash(persona_id: str, institucion_id: str, titulo_obtenido: str,
                   fecha_fin: str, hash_anterior: str, nonce: int) -> str:
    """
    Genera el SHA256 del bloque concatenando sus campos clave.
    Si cualquier dato cambia, el hash cambia completamente (inmutabilidad).
    """
    contenido = f"{persona_id}{institucion_id}{titulo_obtenido}{fecha_fin}{hash_anterior}{nonce}"
    return hashlib.sha256(contenido.encode()).hexdigest()

def proof_of_work(persona_id: str, institucion_id: str, titulo_obtenido: str,
                   fecha_fin: str, hash_anterior: str) -> tuple[int, str]:
    """
    Proof of Work: itera el nonce hasta encontrar un hash que inicie con DIFFICULTY.
    Esto simula el 'minado' y hace costoso alterar la cadena.
    
    Returns:
        (nonce, hash_valido)
    """
    nonce = 0
    logger.info(f"⛏  Iniciando minado... Dificultad: {DIFFICULTY}")
    
    while True:
        hash_resultado = calcular_hash(
            persona_id, institucion_id, titulo_obtenido,
            fecha_fin, hash_anterior, nonce
        )
        # Verificamos si cumple la dificultad
        if hash_resultado.startswith(DIFFICULTY):
            logger.info(f"✅ Bloque minado! Nonce: {nonce} | Hash: {hash_resultado[:20]}...")
            return nonce, hash_resultado
        nonce += 1

def validar_proof(persona_id: str, institucion_id: str, titulo_obtenido: str,
                   fecha_fin: str, hash_anterior: str, nonce: int, hash_actual: str) -> bool:
    """
    Valida que el hash de un bloque recibido sea correcto y cumpla la dificultad.
    Los demás nodos usan esto al recibir un bloque propagado.
    """
    hash_calculado = calcular_hash(
        persona_id, institucion_id, titulo_obtenido,
        fecha_fin, hash_anterior, nonce
    )
    es_valido = hash_calculado == hash_actual and hash_actual.startswith(DIFFICULTY)
    
    if not es_valido:
        logger.warning(f"⚠  Bloque INVÁLIDO. Hash recibido: {hash_actual[:20]}...")
    
    return es_valido

def validar_cadena(cadena: list) -> bool:
    """
    Recorre toda la cadena verificando:
    1. Que el hash_anterior de cada bloque coincide con el hash_actual del anterior.
    2. Que el Proof of Work de cada bloque es válido.
    
    Esto garantiza la integridad de la blockchain completa.
    """
    if not cadena:
        return True
    
    for i in range(1, len(cadena)):
        bloque_actual = cadena[i]
        bloque_anterior = cadena[i - 1]
        
        # Regla 1: El hash anterior debe coincidir
        if bloque_actual.get("hash_anterior") != bloque_anterior.get("hash_actual"):
            logger.error(f"❌ Cadena rota en bloque {i}: hash_anterior no coincide")
            return False
        
        # Regla 2: El Proof of Work debe ser válido
        if not validar_proof(
            bloque_actual.get("persona_id", ""),
            bloque_actual.get("institucion_id", ""),
            bloque_actual.get("titulo_obtenido", ""),
            str(bloque_actual.get("fecha_fin", "")),
            bloque_actual.get("hash_anterior", ""),
            bloque_actual.get("nonce", 0),
            bloque_actual.get("hash_actual", "")
        ):
            logger.error(f"❌ PoW inválido en bloque {i}")
            return False
    
    logger.info(f"✅ Cadena válida con {len(cadena)} bloques")
    return True
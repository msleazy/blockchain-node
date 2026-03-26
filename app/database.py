# app/database.py
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Inicializa el cliente de Supabase usando variables de entorno
def get_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("❌ SUPABASE_URL y SUPABASE_KEY son requeridos en .env")
    
    return create_client(url, key)

# Instancia global reutilizable
supabase: Client = get_client()
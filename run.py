# run.py
import os
from dotenv import load_dotenv
from app import create_app

load_dotenv()

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("NODE_PORT", 8001))
    node_id = os.getenv("NODE_ID", "nodo-desconocido")
    
    print(f"""
╔══════════════════════════════════════╗
║   🔗 Blockchain Node iniciado        ║
║   ID:     {node_id:<27}║
║   Puerto: {port:<27}║
║   Docs:   http://localhost:{port}/docs  ║
╚══════════════════════════════════════╝
    """)
    
    app.run(host="0.0.0.0", port=port, debug=True)
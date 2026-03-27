📄 README.md para tu Repositorio
Aquí está el README completo, cópialo y pégalo en un archivo README.md en la raíz del proyecto:
# 🔗 Blockchain Node — Red de Grados Académicos

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)
![Swagger](https://img.shields.io/badge/Swagger-OpenAPI-85EA2D?style=for-the-badge&logo=swagger&logoColor=black)

Nodo independiente de una red blockchain distribuida para la gestión y validación
de grados académicos. Cada nodo expone una API REST, implementa Proof of Work,
se comunica con otros nodos y persiste los datos en Supabase.

---

## 📋 Tabla de Contenidos

- [Arquitectura](#-arquitectura)
- [Tecnologías](#-tecnologías)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Base de Datos](#-base-de-datos)
- [Ejecución](#-ejecución)
- [API Endpoints](#-api-endpoints)
- [Lógica Blockchain](#-lógica-blockchain)
- [Fases del Proyecto](#-fases-del-proyecto)
- [Estructura del Proyecto](#-estructura-del-proyecto)

---

## 🏗 Arquitectura

     ┌─────────────────┐
     │   NODO MARIANO  │  :8001
     │   (Flask API)   │
     └────────┬────────┘
              │  Comunica y propaga
    ┌─────────┼──────────┐
    ▼         ▼          ▼

   Nodo :8002  Nodo :8003  Nodo :XXXX
   (Laravel)  (Next.js)   (Express)
   Todos conectados a su propia instancia de Supabase

Cada nodo es **autónomo e independiente**. La red sigue funcionando
aunque uno o más nodos fallen.

---

## 🛠 Tecnologías

| Capa | Tecnología |
|---|---|
| Backend | Python 3.11+ / Flask 3.x |
| Base de Datos | Supabase (PostgreSQL) |
| Autenticación PoW | SHA-256 |
| Documentación | Swagger UI / OpenAPI 3.0 |
| Comunicación | HTTP REST (requests) |
| Variables de Entorno | python-dotenv |

---

## ✅ Requisitos Previos

- Python **3.11+**
- pip / venv
- Cuenta en [Supabase](https://supabase.com)
- GCC instalado (para compilar dependencias)

# Fedora / RHEL
sudo dnf install gcc gcc-c++ python3-devel make -y

# Ubuntu / Debian
sudo apt install build-essential python3-dev -y


🚀 Instalación
# 1. Clonar el repositorio
git clone https://github.com/msleazy/blockchain-node.git
cd blockchain-node

# 2. Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate       # Linux / macOS
# venv\Scripts\activate        # Windows

# 3. Instalar dependencias
pip install -r requirements.txt


⚙️ Configuración
Crea un archivo .env en la raíz del proyecto:
# Supabase (Project Settings → API)
SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
SUPABASE_KEY=tu_anon_key_aqui

# Identidad de este nodo
NODE_ID=nodo-mariano
NODE_PORT=8001


⚠️ Nunca subas el .env a GitHub. Ya está incluido en el .gitignore.


🗄 Base de Datos
Ejecuta el siguiente SQL en el SQL Editor de Supabase:
-- Personas
CREATE TABLE personas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(100) NOT NULL,
    apellido_paterno VARCHAR(100) NOT NULL,
    apellido_materno VARCHAR(100),
    curp VARCHAR(18) UNIQUE,
    correo VARCHAR(150),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Instituciones
CREATE TABLE instituciones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(255) NOT NULL,
    pais VARCHAR(100),
    estado VARCHAR(100),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Niveles de Grado
CREATE TABLE niveles_grado (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);
INSERT INTO niveles_grado (nombre) VALUES
('Técnico'),('Licenciatura'),('Maestría'),('Doctorado'),('Especialidad');

-- Programas
CREATE TABLE programas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(255) NOT NULL,
    nivel_grado_id INT REFERENCES niveles_grado(id),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Grados (Bloques de la Blockchain)
CREATE TABLE grados (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    persona_id UUID REFERENCES personas(id) ON DELETE CASCADE,
    institucion_id UUID REFERENCES instituciones(id),
    programa_id UUID REFERENCES programas(id),
    fecha_inicio DATE,
    fecha_fin DATE,
    titulo_obtenido VARCHAR(255),
    numero_cedula VARCHAR(50),
    titulo_tesis TEXT,
    menciones VARCHAR(100),
    hash_actual TEXT NOT NULL,
    hash_anterior TEXT,
    nonce INTEGER,
    firmado_por VARCHAR(255),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Nodos registrados
CREATE TABLE nodos (
    id SERIAL PRIMARY KEY,
    url VARCHAR(255) UNIQUE NOT NULL,
    registrado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transacciones pendientes de minar
CREATE TABLE transacciones_pendientes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    persona_id UUID,
    institucion_id UUID,
    programa_id UUID,
    fecha_inicio DATE,
    fecha_fin DATE,
    titulo_obtenido VARCHAR(255),
    numero_cedula VARCHAR(50),
    titulo_tesis TEXT,
    menciones VARCHAR(100),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


▶️ Ejecución
# Activar entorno virtual
source venv/bin/activate

# Iniciar el nodo
python run.py

Salida esperada:
╔══════════════════════════════════════╗
║   🔗 Blockchain Node iniciado        ║
║   ID:     nodo-mariano               ║
║   Puerto: 8001                       ║
║   Docs:   http://localhost:8001/docs ║
╚══════════════════════════════════════╝

Documentación Swagger disponible en:
http://localhost:8001/docs


📡 API Endpoints



Método
Endpoint
Descripción



GET
/health
Estado del nodo


GET
/chain
Retorna la cadena completa


POST
/transactions
Crear transacción y propagarla


POST
/mine
Minar bloque y propagarlo


POST
/blocks/receive
Recibir bloque de otro nodo


POST
/nodes/register
Registrar un nodo en la red


GET
/nodes
Listar nodos registrados


GET
/nodes/resolve
Ejecutar algoritmo de consenso


GET
/docs
Swagger UI


Ejemplos de uso
# Health check
curl http://localhost:8001/health

# Ver la cadena
curl http://localhost:8001/chain

# Crear transacción
curl -X POST http://localhost:8001/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "persona_id": "uuid-persona",
    "institucion_id": "uuid-institucion",
    "programa_id": "uuid-programa",
    "titulo_obtenido": "Ingeniero en Sistemas",
    "fecha_fin": "2024-06-01"
  }'

# Minar un bloque
curl -X POST http://localhost:8001/mine

# Registrar otro nodo
curl -X POST http://localhost:8001/nodes/register \
  -H "Content-Type: application/json" \
  -d '{"url": "http://localhost:8002"}'

# Resolver conflictos (consenso)
curl http://localhost:8001/nodes/resolve


⛓ Lógica Blockchain
Cálculo del Hash
Cada bloque genera su hash con SHA-256 a partir de:
hash = SHA256(
  persona_id +
  institucion_id +
  titulo_obtenido +
  fecha_fin +
  hash_anterior +
  nonce
)

Proof of Work
El nonce se incrementa hasta que el hash cumpla la dificultad establecida:
DIFFICULTY = "000"

while not hash.startswith(DIFFICULTY):
    nonce += 1
    hash = calcular_hash(..., nonce)

Algoritmo de Consenso (Longest Chain Rule)
Cuando dos nodos minan simultáneamente y surge un conflicto, 
GET /nodes/resolve consulta la cadena de todos los nodos registrados
y adopta la cadena válida más larga:
Nodo A: [G] → [1] → [2] → [3]        ← GANA ✅
Nodo B: [G] → [1] → [2]


🗺 Fases del Proyecto

 Fase 1 — Setup: API funcional en puerto :8001
 Fase 2 — Registro: Endpoints de comunicación inter-nodos
 Fase 3 — Pruebas de Red: Propagación de transacciones y bloques
 Fase 4 — Consenso: Resolución de conflictos distribuida


📁 Estructura del Proyecto
blockchain-node/
├── app/
│   ├── __init__.py          # Factory de la app Flask
│   ├── blockchain.py        # Lógica core (hash, PoW, consenso)
│   ├── database.py          # Cliente Supabase
│   └── routes/
│       ├── chain.py         # GET /chain
│       ├── transactions.py  # POST /transactions
│       ├── mine.py          # POST /mine
│       └── nodes.py         # /nodes/*
├── .env                     # Variables de entorno (no commitear)
├── .gitignore
├── openapi.yaml             # Especificación OpenAPI
├── requirements.txt
└── run.py                   # Entry point


👤 Autor
Mariano — Nodo independiente dentro de la Red BlockchainMateria: Tópicos Avanzados de Desarrollo Web y Móvil


🔒 Este nodo es autónomo. La red continúa operando aunque este nodo esté offline.

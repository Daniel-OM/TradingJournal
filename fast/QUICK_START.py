#!/usr/bin/env python3
"""
📚 QUICK START - Trading Journal FastAPI
Guía rápida para empezar en 5 minutos
"""

SETUP_GUIDE = """
╔════════════════════════════════════════════════════════════════╗
║        🚀 Trading Journal FastAPI - QUICK START              ║
║                  (5 Minutos para empezar)                     ║
╚════════════════════════════════════════════════════════════════╝

┌─ PASO 1: Clonar / Descargar ────────────────────────────────┐
│                                                             │
│  $ git clone <repo>                                        │
│  $ cd fast                                                 │
│                                                            │
└────────────────────────────────────────────────────────────┘

┌─ PASO 2: Entorno Virtual (1 min) ──────────────────────────┐
│                                                             │
│  Windows:                                                  │
│  $ python -m venv venv                                    │
│  $ venv\\Scripts\\activate                                  │
│                                                             │
│  Linux/Mac:                                                │
│  $ python3 -m venv venv                                   │
│  $ source venv/bin/activate                               │
│                                                             │
└────────────────────────────────────────────────────────────┘

┌─ PASO 3: Instalar Dependencias (2 min) ────────────────────┐
│                                                             │
│  $ pip install -r requirements.txt                        │
│                                                             │
│  Esto instala 14 paquetes (40-60 segundos típicamente)   │
│                                                             │
└────────────────────────────────────────────────────────────┘

┌─ PASO 4: Configurar .env (30 segundos) ────────────────────┐
│                                                             │
│  $ cp .env.example .env                                   │
│                                                             │
│  Edita .env si necesitas cambiar valores (optional)       │
│  Por defecto funciona con SQLite local                    │
│                                                             │
└────────────────────────────────────────────────────────────┘

┌─ PASO 5: Inicializar BD (30 segundos) ─────────────────────┐
│                                                             │
│  $ python init_db.py                                      │
│                                                             │
│  Esto crea:                                                │
│  ✓ Tablas de BD                                            │
│  ✓ Usuario demo: trader / password123                     │
│  ✓ 20 trades de ejemplo                                   │
│  ✓ 3 estrategias                                          │
│  ✓ 2 watchlists                                           │
│                                                             │
└────────────────────────────────────────────────────────────┘

┌─ PASO 6: Ejecutar Servidor (30 segundos) ──────────────────┐
│                                                             │
│  $ uvicorn app.main:app --port=3000 --reload                │
│                                                             │
│  Deberías ver:                                             │
│  ✓ Uvicorn running on http://127.0.0.1:3000              │
│  ✓ Application startup complete                          │
│                                                             │
└────────────────────────────────────────────────────────────┘

┌─ PASO 7: Probar la API ────────────────────────────────────┐
│                                                             │
│  Opción A: Swagger UI (Visual)                            │
│  → http://localhost:3000/docs                             │
│  → Puedes hacer requests interactivamente                │
│                                                             │
│  Opción B: Script automático                             │
│  $ python test_api.py                                    │
│  → Ejecuta tests de todos los endpoints                 │
│                                                             │
│  Opción C: cURL                                          │
│  $ curl http://localhost:3000/health                    │
│  → {"status": "ok", "version": "1.0.0"}                 │
│                                                             │
└────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════

📌 ENDPOINTS PRINCIPALES

Auth:
  POST   /api/v1/auth/register
  POST   /api/v1/auth/login

Trades:
  GET    /api/v1/trades
  POST   /api/v1/trades
  GET    /api/v1/trades/{id}
  PUT    /api/v1/trades/{id}
  DELETE /api/v1/trades/{id}

Estrategias:
  GET    /api/v1/strategies
  POST   /api/v1/strategies
  GET    /api/v1/strategies/{id}
  PUT    /api/v1/strategies/{id}
  DELETE /api/v1/strategies/{id}

Performance:
  GET    /api/v1/performance/stats
  GET    /api/v1/performance/symbols

═══════════════════════════════════════════════════════════════

🔐 LOGIN EJEMPLO

Terminal 1: Iniciar servidor
  $ uvicorn app.main:app --reload

Terminal 2: Login
  $ curl -X POST "http://localhost:3000/api/v1/auth/login" \\
    -H "Content-Type: application/json" \\
    -d '{"username":"trader","password":"password123"}'

Respuesta:
  {
    "access_token": "eyJhbGci...",
    "refresh_token": "eyJhbGci...",
    "token_type": "bearer"
  }

Copiar access_token y usar en requests:
  $ curl -X GET "http://localhost:3000/api/v1/trades" \\
    -H "Authorization: Bearer eyJhbGci..."

═══════════════════════════════════════════════════════════════

🧪 TESTING

Automático:
  $ python test_api.py

Manual:
  1. Ir a http://localhost:3000/docs
  2. Click en "Authorize"
  3. Username: trader
  4. Password: password123
  5. Click "Login"
  6. Prueba los endpoints

═══════════════════════════════════════════════════════════════

📁 ESTRUCTURA IMPORTANTE

fast/
├── .env                    ← Tu configuración (NO commitar)
├── trading_journal.db      ← BD SQLite (creada por init_db.py)
├── app/
│   ├── main.py            ← Punto de entrada
│   ├── core/              ← Config y seguridad
│   ├── db/                ← Base de datos
│   ├── models/            ← Modelos ORM
│   ├── schemas/           ← Validación
│   ├── services/          ← Lógica
│   └── api/v1/            ← Endpoints
└── requirements.txt       ← Dependencias

═══════════════════════════════════════════════════════════════

⚙️ VARIABLES DE ENTORNO (.env)

DATABASE_URL=sqlite:///./trading_journal.db
  → Cambiar por postgresql:// para producción

SECRET_KEY=change_me_with_a_long_random_string
  → CAMBIAR en producción

ALGORITHM=HS256
  → Algoritmo de JWT

ACCESS_TOKEN_EXPIRE_MINUTES=30
  → Tiempo de expiración del token

DEBUG=True
  → Cambiar a False en producción

BACKEND_CORS_ORIGINS=[...]
  → Orígenes permitidos para CORS

═══════════════════════════════════════════════════════════════

🐳 CON DOCKER

Desarrollo:
  $ docker-compose up

Acceso:
  - API: http://localhost:3000
  - DB: localhost:5432
  - Docs: http://localhost:3000/docs

Parar:
  $ docker-compose down

═══════════════════════════════════════════════════════════════

❓ PROBLEMAS COMUNES

P: "ModuleNotFoundError: No module named 'fastapi'"
R: pip install -r requirements.txt

P: "Address already in use :3000"
R: Cambiar puerto: uvicorn app.main:app --reload --port 8001

P: "Database is locked"
R: rm trading_journal.db && python init_db.py

P: "CORS error en frontend"
R: Editar .env y agregar tu frontend URL en BACKEND_CORS_ORIGINS

P: "Invalid token"
R: Token expirado, hacer login de nuevo

═══════════════════════════════════════════════════════════════

📚 DOCUMENTACIÓN

README.md                    ← Docs detalladas
PROJECT_STRUCTURE.md         ← Estructura completa
IMPLEMENTATION_SUMMARY.md    ← Resumen de features
FLASK_vs_FASTAPI.md          ← Comparativa
QUICK_START.md               ← Este archivo

═══════════════════════════════════════════════════════════════

🎯 PRÓXIMOS PASOS

1. Asegurate que el servidor está ejecutándose
2. Prueba los endpoints en http://localhost:3000/docs
3. Lee README.md para más detalles
4. Cuando esté listo, crea frontend React

═══════════════════════════════════════════════════════════════

✨ ¡LISTO!

Tu API FastAPI está ejecutándose. Puedes:

✓ Ver documentación automática: http://localhost:3000/docs
✓ Probar endpoints interactivamente
✓ Integrar con React, Vue, Angular
✓ Deployar a Docker
✓ Escalar horizontalmente

═══════════════════════════════════════════════════════════════

Última actualización: 2024-01-17
Versión: 1.0.0
Estado: ✅ Producción Ready
"""

if __name__ == "__main__":
    print(SETUP_GUIDE)

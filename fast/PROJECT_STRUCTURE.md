# FastAPI Project Structure - Trading Journal

## 📋 Resumen

Este documento describe la estructura completa del proyecto FastAPI para Trading Journal.

## 🗂️ Estructura de Carpetas

```
fast/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Punto de entrada principal
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Configuración (Pydantic Settings)
│   │   └── security.py         # Autenticación y seguridad (JWT, passwords)
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py         # Configuración SQLAlchemy
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py           # Modelos ORM (11 tablas)
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── schemas.py          # Esquemas Pydantic para validación
│   ├── services/
│   │   ├── __init__.py
│   │   └── performance.py      # Calculadoras de estadísticas
│   └── api/
│       ├── __init__.py
│       └── v1/
│           ├── __init__.py
│           └── endpoints.py    # Todos los endpoints de la API
├── .env                        # Variables de entorno (NO COMMITEAR)
├── .env.example                # Plantilla de .env
├── .gitignore                  # Archivos ignorados en Git
├── requirements.txt            # Dependencias Python
├── pyproject.toml              # Configuración del proyecto
├── README.md                   # Documentación principal
├── Dockerfile                  # Configuración Docker
├── docker-compose.yml          # Orquestación de contenedores
├── gunicorn_config.py          # Configuración Gunicorn (producción)
├── init_db.py                  # Script para inicializar BD con datos
├── test_api.py                 # Script de testing de endpoints
└── .github/
    └── workflows/
        └── tests.yml           # CI/CD pipeline (GitHub Actions)
```

## 🔧 Componentes Principales

### 1. **Core** (`app/core/`)
Módulos de configuración y seguridad.

#### `config.py`
- `Settings`: Clase Pydantic para cargar variables de entorno
- Variables: DATABASE_URL, SECRET_KEY, CORS_ORIGINS, etc.
- Soporta archivos `.env`

#### `security.py`
- `hash_password()`: Hashea contraseñas con bcrypt
- `verify_password()`: Verifica contraseñas
- `create_access_token()`: Crea tokens JWT
- `create_refresh_token()`: Crea refresh tokens
- `get_current_user()`: Dependency para validar tokens en endpoints

### 2. **Database** (`app/db/`)

#### `database.py`
- `engine`: Motor SQLAlchemy con conexión a BD
- `SessionLocal`: Factory para crear sesiones
- `Base`: Clase base para modelos ORM
- `get_db()`: Dependency para inyectar sesión en endpoints

### 3. **Models** (`app/models/`)

#### `models.py` - 11 Modelos ORM:

| Modelo | Descripción |
|--------|-------------|
| `User` | Usuario del sistema |
| `Trade` | Transacción comercial (CRUD principal) |
| `Strategy` | Estrategia de trading |
| `StrategyCondition` | Condiciones dentro de una estrategia |
| `Transaction` | Detalles de ejecución de un trade |
| `Media` | Archivos/imágenes asociados a trades |
| `Error` | Registro de errores y excepciones |
| `Watchlist` | Lista de observación de activos |
| `WatchlistEntry` | Entrada individual en una watchlist |
| `Candle` | Datos OHLCV de velas |
| `Setting` | Configuración personalizada del usuario |

**Tablas de asociación:**
- `trade_scoring`: Vincula trades con strategy conditions
- `trade_errors`: Vincula trades con errores (con impacto)

### 4. **Schemas** (`app/schemas/`)

#### `schemas.py` - Validación Pydantic

**Grupos de esquemas:**
- **Auth**: LoginRequest, TokenResponse
- **User**: UserCreate, UserUpdate, UserResponse
- **Trade**: TradeCreate, TradeUpdate, TradeResponse
- **Strategy**: StrategyCreate, StrategyUpdate, StrategyResponse
- **Watchlist**: WatchlistCreate, WatchlistUpdate, WatchlistResponse
- **Performance**: PerformanceStats, BestWorstSymbols

**Características:**
- `from_attributes = True` para ORM mode
- Validación automática en requests/responses
- Separación entre modelos DB y schemas API

### 5. **Services** (`app/services/`)

#### `performance.py`
**Clases:**

1. **PerformanceCalculator**
   - Calcula estadísticas agregadas de todos los trades
   - Retorna: total_pnl, win_rate, sharpe_ratio, max_drawdown, etc.
   - Métodos: `_mean()`, `_std()`, `calculate_streaks()`

2. **SymbolPerformanceCalculator**
   - Calcula estadísticas por símbolo
   - Retorna: mejores 5 y peores 5 activos
   - Datos por símbolo: total_pnl, avg_pnl, win_rate, trade_count

### 6. **API** (`app/api/v1/`)

#### `endpoints.py` - Todos los endpoints

**Estructura de endpoints:**

```
POST   /auth/register         - Registrar usuario
POST   /auth/login            - Login (obtener tokens)
GET    /users/me              - Datos del usuario actual

POST   /trades                - Crear trade
GET    /trades                - Listar trades (con filtros)
GET    /trades/{id}           - Obtener trade específico
PUT    /trades/{id}           - Actualizar trade
DELETE /trades/{id}           - Eliminar trade

POST   /strategies            - Crear estrategia
GET    /strategies            - Listar estrategias
GET    /strategies/{id}       - Obtener estrategia
PUT    /strategies/{id}       - Actualizar estrategia
DELETE /strategies/{id}       - Eliminar estrategia

POST   /watchlists            - Crear watchlist
GET    /watchlists            - Listar watchlists
GET    /watchlists/{id}       - Obtener watchlist
PUT    /watchlists/{id}       - Actualizar watchlist
DELETE /watchlists/{id}       - Eliminar watchlist

GET    /performance/stats     - Estadísticas generales
GET    /performance/symbols   - Performance por símbolo
```

**Características:**
- Todos los endpoints requieren autenticación (HTTPBearer)
- Filtrado por usuario (user_id del token)
- Validación automática con Pydantic
- Respuestas JSON tipadas
- Códigos de estado HTTP apropiados

### 7. **Main** (`app/main.py`)

#### FastAPI App
- Inicialización con metadata
- CORS middleware (configurable)
- TrustedHostMiddleware
- Tabla creation on startup
- Health endpoint (`/health`)
- Root endpoint (`/`)
- Router principal incluido

## 🚀 Flujo de Datos

### Ejemplo: Crear un Trade

```
1. Cliente →  POST /api/v1/trades
              Headers: Authorization: Bearer {token}
              Body: TradeCreate schema

2. FastAPI → validate request with TradeCreate

3. Endpoint → 
   - Extract user_id from token (get_current_user)
   - Get DB session (get_db dependency)
   - Create ORM Trade object with user_id
   - Add to session and commit

4. Database → Save to trades table

5. Response → TradeResponse schema
              Status 200 + trade data
```

## 🔐 Seguridad

### Autenticación
- JWT tokens en Authorization header
- Access token (corta duración: 30 min default)
- Refresh token (larga duración: 7 días default)

### Contraseñas
- Hasheadas con bcrypt
- Never stored in plain text

### CORS
- Configurable por entorno
- Default: localhost:3000, localhost:5173

### Data Isolation
- Cada usuario solo ve sus propios trades
- Filtrado por `user_id` en queries

## 📊 Base de Datos

### Tipos de BD soportados
- **SQLite** (default, desarrollo)
- **PostgreSQL** (producción)

### Variables de entorno
```
DATABASE_URL=sqlite:///./trading_journal.db
# O: postgresql://user:password@localhost/trading_journal
```

### Migraciones
- Actualmente: auto-create on startup
- Futura: Alembic para migraciones controladas

## 🧪 Testing

### Scripts incluidos

**`init_db.py`**
- Crea usuario de ejemplo: `trader` / `password123`
- Genera 20 trades de ejemplo
- Crea 3 estrategias
- Crea 2 watchlists
- Uso: `python init_db.py`

**`test_api.py`**
- Suite de pruebas de todos los endpoints
- Tests: register, login, trades, strategies, watchlists
- Uso: `python test_api.py`
- Requiere servidor ejecutándose

## 🐳 Docker

### Desarrollo
```bash
docker-compose up
```
- API en `http://localhost:3000`
- PostgreSQL en `localhost:5432`

### Producción
```bash
docker build -t trading-journal-api .
docker run -p 3000:3000 trading-journal-api
```

## 📦 Dependencias Principales

| Paquete | Versión | Uso |
|---------|---------|-----|
| fastapi | 0.109.0 | Framework web |
| uvicorn | 0.27.0 | ASGI server |
| sqlalchemy | 2.0.24 | ORM |
| pydantic | 2.5.3 | Validación |
| python-jose | 3.3.0 | JWT |
| passlib | 1.7.4 | Password hashing |
| python-multipart | 0.0.6 | Form uploads |

## 🎯 Próximos Pasos

### Pendiente en V1.1
- [ ] File upload endpoint para media
- [ ] Candle sync desde Yahoo Finance / Benzinga
- [ ] Más endpoints de performance (monthly, weekly)
- [ ] Export PDF de reportes
- [ ] Notificaciones por email

### Pendiente en V2.0
- [ ] Migraciones con Alembic
- [ ] WebSockets para datos en tiempo real
- [ ] Rate limiting
- [ ] Admin dashboard
- [ ] API keys vs OAuth2
- [ ] Webhook para integraciones externas

## 📚 Documentación del Cliente

Ver archivos en `fast/`:
- `README.md` - Guía de instalación y uso
- `.env.example` - Plantilla de variables
- `Dockerfile` + `docker-compose.yml` - Deployment

## 🤝 Contribución

1. Crear rama: `git checkout -b feature/nombre`
2. Commit: `git commit -m "Descripción"`
3. Push: `git push origin feature/nombre`
4. PR a `main`

## 📝 Licencia

MIT (ver archivo LICENSE si existe)

---

**Última actualización:** 2024-01-17
**Versión:** 1.0.0
**Estado:** ✅ Listo para desarrollo

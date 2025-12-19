# Trading Journal API - FastAPI

API RESTful para la aplicación de Trading Journal, construida con FastAPI.

## Requisitos

- Python 3.8+
- pip

## Instalación

### 1. Crear un entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Crear un archivo `.env` en la raíz del proyecto (copiar de `.env.example`):

```bash
DATABASE_URL=sqlite:///./trading_journal.db
SECRET_KEY=tu_clave_secreta_muy_segura_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
DEBUG=True
APP_NAME=Trading Journal API
APP_VERSION=1.0.0
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"]
UPLOAD_FOLDER=./instance/media/
```

### 4. Inicializar la base de datos

Las tablas se crean automáticamente al iniciar la aplicación.

## Uso

### Iniciar el servidor

```bash
# En desarrollo (con auto-reload)
uvicorn app.main:app --port=3000 --reload

# O directamente desde Python
python -m uvicorn app.main:app --port=3000 --reload
```

El servidor estará disponible en: `http://localhost:3000`

### Acceder a la documentación interactiva

- **Swagger UI**: http://localhost:3000/docs
- **ReDoc**: http://localhost:3000/redoc

## Estructura del Proyecto

```
fast/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Entrada principal de FastAPI
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Configuración y variables de entorno
│   │   └── security.py         # JWT y funciones de autenticación
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py         # Configuración de SQLAlchemy
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py           # Modelos SQLAlchemy ORM
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── schemas.py          # Esquemas Pydantic para validación
│   ├── services/
│   │   ├── __init__.py
│   │   └── performance.py      # Lógica de cálculo de performance
│   └── api/
│       ├── __init__.py
│       └── v1/
│           ├── __init__.py
│           └── endpoints.py    # Endpoints de la API v1
├── requirements.txt            # Dependencias Python
└── README.md                   # Este archivo
```

## API Endpoints

### Autenticación

- `POST /api/v1/auth/register` - Registrar nuevo usuario
- `POST /api/v1/auth/login` - Login (obtener tokens)

### Trades

- `GET /api/v1/trades` - Listar todos los trades
- `POST /api/v1/trades` - Crear nuevo trade
- `GET /api/v1/trades/{id}` - Obtener un trade específico
- `PUT /api/v1/trades/{id}` - Actualizar un trade
- `DELETE /api/v1/trades/{id}` - Eliminar un trade

### Estrategias

- `GET /api/v1/strategies` - Listar todas las estrategias
- `POST /api/v1/strategies` - Crear nueva estrategia
- `GET /api/v1/strategies/{id}` - Obtener una estrategia específica
- `PUT /api/v1/strategies/{id}` - Actualizar una estrategia
- `DELETE /api/v1/strategies/{id}` - Eliminar una estrategia

### Watchlists

- `GET /api/v1/watchlists` - Listar todas las watchlists
- `POST /api/v1/watchlists` - Crear nueva watchlist
- `GET /api/v1/watchlists/{id}` - Obtener una watchlist específica
- `PUT /api/v1/watchlists/{id}` - Actualizar una watchlist
- `DELETE /api/v1/watchlists/{id}` - Eliminar una watchlist

### Performance

- `GET /api/v1/performance/stats` - Obtener estadísticas de performance
- `GET /api/v1/performance/symbols` - Obtener performance por símbolo (mejores/peores)

### Salud

- `GET /health` - Health check del servidor
- `GET /` - Información general de la API

## Ejemplos de Uso

### Registrarse

```bash
curl -X POST "http://localhost:3000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "trader123",
    "email": "trader@example.com",
    "password": "segura_password_123"
  }'
```

### Login

```bash
curl -X POST "http://localhost:3000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "trader123",
    "password": "segura_password_123"
  }'
```

Respuesta:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Crear un Trade

```bash
curl -X POST "http://localhost:3000/api/v1/trades" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {access_token}" \
  -d '{
    "symbol": "AAPL",
    "entry_date": "2024-01-15",
    "entry_price": 150.50,
    "quantity": 100,
    "trade_type": "LONG",
    "exit_date": "2024-01-16",
    "exit_price": 152.00,
    "exit_quantity": 100,
    "profit_loss": 150.00,
    "commission": 10.00,
    "description": "Trade de ejemplo"
  }'
```

### Obtener Performance

```bash
curl -X GET "http://localhost:3000/api/v1/performance/stats?gross=false" \
  -H "Authorization: Bearer {access_token}"
```

## Autenticación

La API utiliza autenticación JWT (JSON Web Tokens). Para acceder a endpoints protegidos:

1. Hacer login con `POST /auth/login` para obtener un token
2. Incluir el token en todas las peticiones en el header: `Authorization: Bearer {token}`

El token expira según `ACCESS_TOKEN_EXPIRE_MINUTES` en la configuración.

## Variables de Entorno

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `DATABASE_URL` | URL de conexión a la BD | sqlite:///./trading_journal.db |
| `SECRET_KEY` | Clave secreta para JWT | change_me |
| `ALGORITHM` | Algoritmo de JWT | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiración del token | 30 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Expiración del refresh token | 7 |
| `DEBUG` | Modo debug | False |
| `APP_NAME` | Nombre de la aplicación | Trading Journal API |
| `APP_VERSION` | Versión de la app | 1.0.0 |
| `BACKEND_CORS_ORIGINS` | Orígenes CORS permitidos | [] |
| `UPLOAD_FOLDER` | Carpeta para uploads | ./instance/media/ |

## Desarrollo

### Ejecutar tests

```bash
pytest
```

### Verificar código

```bash
# Linting
flake8 app

# Type checking
mypy app
```

## Integración con Frontend

### React

Para conectar un frontend React:

1. Instalar dependencias CORS en el servidor (ya incluidas)
2. En React, configurar el proxy o usar fetch/axios:

```javascript
const API_URL = 'http://localhost:3000/api/v1';

// Login
const response = await fetch(`${API_URL}/auth/login`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'user', password: 'pass' })
});

const { access_token } = await response.json();

// Usar token en requests posteriores
const trades = await fetch(`${API_URL}/trades`, {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
```

## Troubleshooting

### CORS errors

Si obtienes errores de CORS:
- Verifica que `BACKEND_CORS_ORIGINS` incluya la URL de tu frontend
- En desarrollo, agrega `http://localhost:3000` y `http://localhost:5173`

### Database locked

Si la BD está bloqueada:
```bash
# Eliminar archivo de BD y reiniciar
rm trading_journal.db
```

### Import errors

Si faltan dependencias:
```bash
pip install -r requirements.txt
```

## Contribuir

Para contribuir al proyecto:

1. Crear una rama desde `main`
2. Hacer commit de los cambios
3. Crear un Pull Request

## Licencia

Ver archivo LICENSE

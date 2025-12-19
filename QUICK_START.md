# 🚀 Trading Journal - Guía de Inicio Rápido

Una aplicación completa de diario de trading con backend FastAPI y frontend React.

## 📋 Requisitos Previos

- Python 3.9+
- Node.js 16+
- npm 8+
- PostgreSQL 12+ (opcional, puede usar SQLite para desarrollo)

## 🎯 Instalación Rápida

### 1. Clonar el Proyecto

```bash
cd /path/to/TradingJournal
```

### 2. Configurar Backend (FastAPI)

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno (si es necesario)
# Ver archivo: .env o .env.example

# Inicializar la base de datos
python -c "from journal.app import init_db; init_db()"

# Ejecutar el servidor FastAPI
python -m uvicorn journal.app:app --reload --host 0.0.0.0 --port 8000
```

El backend estará disponible en: **http://localhost:8000**

### 3. Configurar Frontend (React)

```bash
cd front

# Instalar dependencias
npm install

# Crear archivo .env
cp .env.example .env

# Ejecutar servidor de desarrollo
npm run dev
```

El frontend estará disponible en: **http://localhost:5173**

## 🎨 Estructura del Proyecto

```
TradingJournal/
├── journal/                    # Backend FastAPI
│   ├── app.py                 # Aplicación principal
│   ├── models/                # Modelos de datos
│   │   └── entities/          # Entidades separadas
│   ├── schemas/               # Esquemas Pydantic
│   │   └── entities/          # Esquemas separados
│   ├── api/v1/                # API v1
│   │   └── routes/            # Routers por recurso
│   ├── routers/               # Routers legacy (deprecated)
│   └── templates/             # Templates Flask (deprecated)
├── front/                     # Frontend React
│   ├── src/
│   │   ├── pages/            # Páginas principales
│   │   ├── components/       # Componentes reutilizables
│   │   ├── services/         # Servicios API
│   │   ├── store/            # Estado global (Zustand)
│   │   ├── types/            # Tipos TypeScript
│   │   ├── App.tsx           # Configuración de rutas
│   │   └── main.tsx          # Entry point
│   ├── tailwind.config.js    # Configuración Tailwind
│   ├── postcss.config.js     # Configuración PostCSS
│   ├── vite.config.ts        # Configuración Vite
│   └── package.json
├── migrations/               # Migrations Alembic
├── requirements.txt          # Dependencias Python
└── README.md
```

## 📚 Páginas Disponibles

### Frontend React

**Públicas (sin autenticación):**
- `/` - Página de inicio
- `/login` - Iniciar sesión
- `/register` - Crear cuenta

**Privadas (requieren autenticación):**
- `/dashboard` - Panel de control
- `/trades` - Gestión de operaciones
- `/strategies` - Gestión de estrategias
- `/watchlists` - Gestión de listas de vigilancia
- `/performance` - Análisis de rendimiento

## 🔐 Sistema de Autenticación

### Backend (FastAPI)
- Endpoint: `POST /api/v1/auth/register`
- Endpoint: `POST /api/v1/auth/login`
- Retorna: `access_token` y `refresh_token` (JWT)

### Frontend (React)
- Usa Zustand para gestionar estado de autenticación
- Almacena tokens en `localStorage`
- Interceptores Axios automáticos para enviar token en cada request
- Protección de rutas con componente `<PrivateRoute>`

## 🛠️ Comandos Principales

### Backend
```bash
# Iniciar servidor (con recarga automática)
python -m uvicorn journal.app:app --reload

# Inicializar base de datos
python -c "from journal.app import init_db; init_db()"

# Ver documentación interactiva de API
# Visita: http://localhost:8000/docs (Swagger)
# Visita: http://localhost:8000/redoc (ReDoc)
```

### Frontend
```bash
# Instalar dependencias
npm install

# Servidor de desarrollo
npm run dev

# Build para producción
npm run build

# Preview de build
npm run preview

# Lint TypeScript
npm run type-check
```

## 📖 Documentación de API

Ver archivo: `API_DOCUMENTATION.md`

Endpoints principales:
- **Auth**: `/api/v1/auth/register`, `/api/v1/auth/login`
- **Trades**: `/api/v1/trades` (CRUD)
- **Strategies**: `/api/v1/strategies` (CRUD)
- **Watchlists**: `/api/v1/watchlists` (CRUD)
- **Performance**: `/api/v1/performance/stats`, `/api/v1/performance/symbols`

## 🔧 Configuración

### Backend

Archivo: `.env` (en el raíz del proyecto)

```env
# Base de datos
DATABASE_URL=sqlite:///./trading_journal.db

# JWT
SECRET_KEY=tu-clave-secreta-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Frontend

Archivo: `front/.env`

```env
VITE_API_URL=http://localhost:8000/api/v1
```

## 🧪 Testing

### Backend
```bash
# Ejecutar tests (si existen)
pytest

# Con cobertura
pytest --cov=journal
```

### Frontend
```bash
# Tests unitarios
npm run test

# Con cobertura
npm run test:coverage
```

## 📦 Dependencias Principales

### Backend
- FastAPI 0.109.0
- SQLAlchemy 2.0.24
- Pydantic 2.5.3
- python-multipart
- python-jose[cryptography]
- passlib[bcrypt]
- argon2-cffi

### Frontend
- React 18+
- TypeScript
- Vite 7+
- React Router v6
- Axios
- Zustand
- Tailwind CSS 4+

## 🐛 Solución de Problemas

### Backend no responde
```bash
# Verificar que está corriendo en puerto 8000
lsof -i :8000

# Reiniciar servidor
# Presionar Ctrl+C y ejecutar de nuevo
```

### Frontend no conecta a API
```bash
# Verificar URL de API en .env
cat front/.env

# Verificar CORS en backend
# Ver journal/app.py -> CORSMiddleware
```

### Error de base de datos
```bash
# Eliminar base de datos y reinicializar
rm trading_journal.db
python -c "from journal.app import init_db; init_db()"
```

## 🚀 Despliegue

### Backend (Producción)
```bash
# Usar gunicorn
pip install gunicorn
gunicorn journal.app:app -w 4 -b 0.0.0.0:8000
```

### Frontend (Producción)
```bash
# Build
npm run build

# Servir con servidor estático
npx serve -s dist -l 3000
```

## 📞 Soporte

Para reportar problemas o sugerencias:
1. Verificar la sección de "Solución de Problemas"
2. Revisar logs del servidor
3. Consultar documentación de API

## 📝 Licencia

MIT

---

**Versión**: 1.0.0  
**Última actualización**: 2024  
**Autor**: Trading Journal Team

# Trading Journal Frontend

Una aplicación React + TypeScript moderna para rastrear y analizar operaciones de trading.

## 📋 Requisitos

- Node.js 16+ 
- npm 8+
- Backend FastAPI ejecutándose en `http://localhost:8000`

## 🚀 Instalación

1. Instalar dependencias:
```bash
npm install
```

2. Configurar variables de entorno (`.env`):
```bash
VITE_API_URL=http://localhost:8000/api/v1
```

## 🏃 Desarrollo

Para ejecutar el servidor de desarrollo:

```bash
npm run dev
```

La aplicación estará disponible en `http://localhost:5173`

## 🔨 Build

Para crear una build de producción:

```bash
npm run build
```

Para previsualizar la build de producción localmente:

```bash
npm run preview
```

## 📁 Estructura del Proyecto

```
src/
├── components/          # Componentes reutilizables
│   ├── Navbar.tsx      # Barra de navegación
│   ├── FormComponents.tsx  # Inputs de formulario
│   ├── Common.tsx       # Componentes UI comunes
│   ├── PrivateRoute.tsx # Rutas protegidas
│   └── index.ts        # Exportaciones
├── pages/              # Páginas principales
│   ├── HomePage.tsx    # Página de bienvenida
│   ├── LoginPage.tsx   # Login
│   ├── RegisterPage.tsx # Registro
│   ├── DashboardPage.tsx # Dashboard
│   ├── TradesPage.tsx  # Gestión de operaciones
│   ├── StrategiesPage.tsx # Gestión de estrategias
│   ├── WatchlistsPage.tsx # Gestión de watchlists
│   ├── PerformancePage.tsx # Análisis de rendimiento
│   └── index.ts        # Exportaciones
├── services/           # Servicios de API
│   └── api.ts         # Cliente Axios
├── store/             # Estado global
│   └── authStore.ts   # Zustand auth store
├── types/             # Tipos TypeScript
│   └── index.ts       # Interfaces principales
├── App.tsx            # Aplicación principal con router
├── main.tsx           # Entry point
└── index.css          # Estilos con Tailwind
```

## 🔐 Autenticación

La aplicación utiliza un sistema de autenticación basado en tokens JWT:

- **Login**: Envía credenciales y recibe `access_token` y `refresh_token`
- **Almacenamiento**: Los tokens se guardan en `localStorage`
- **Verificación**: Se validan automáticamente en cada petición (interceptor)
- **Protección**: Las rutas privadas están envueltas en `<PrivateRoute>`

## 🎨 Estilos

La aplicación utiliza **Tailwind CSS** para los estilos. Los colores y componentes están predefinidos para consistencia.

### Temas:
- Color primario: Azul (`blue-600`)
- Color de éxito: Verde (`green-500`)
- Color de error: Rojo (`red-500`)
- Fondo: Gris claro (`gray-50`)

## 📚 Páginas Disponibles

### Públicas:
- `/` - Página de inicio
- `/login` - Login
- `/register` - Registro

### Privadas (requieren autenticación):
- `/dashboard` - Panel de control con métricas principales
- `/trades` - Gestión y análisis de operaciones
- `/strategies` - Gestión de estrategias de trading
- `/watchlists` - Gestión de listas de vigilancia
- `/performance` - Análisis detallado de rendimiento

## 🔧 Configuración de TypeScript

- **Strict Mode**: Activado para mayor seguridad de tipos
- **Target**: ES2020
- **JSX**: react-jsx

## 🚀 Características

✅ Autenticación con JWT  
✅ Gestión de operaciones (CRUD)  
✅ Gestión de estrategias  
✅ Análisis de rendimiento  
✅ Componentes reutilizables  
✅ TypeScript para type safety  
✅ Tailwind CSS para estilos modernos  
✅ React Router para navegación  
✅ Zustand para estado global  

## 🤝 Dependencias Principales

- **React 18+**: Framework UI
- **Vite**: Build tool
- **TypeScript**: Type safety
- **React Router v6**: Routing
- **Axios**: HTTP client
- **Zustand**: State management
- **Tailwind CSS**: Utility-first CSS
- **@tailwindcss/postcss**: PostCSS plugin para Tailwind v4

## 📝 Licencia

MIT


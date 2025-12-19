# 📋 GUÍA DE DESARROLLO FUTURO - Trading Journal

## Para la Próxima Sesión

Este documento describe cómo continuar el desarrollo del Trading Journal Frontend.

## 🎯 Orden de Prioridades

### Fase 1: Gráficos (Sesión 2)
**Estimado: 2-3 horas**

1. **Instalar Chart.js**
   ```bash
   npm install chart.js react-chartjs-2
   ```

2. **TradeDetailPage** (`src/pages/TradeDetailPage.tsx`)
   - Mostrar detalles completo del trade
   - Gráfico de velas (OHLC) usando Chart.js
   - Lista de transacciones asociadas
   - Botones editar/eliminar

3. **PerformancePage Mejorada** (`src/pages/PerformancePage.tsx`)
   - Gráfico de P&L acumulado
   - Gráfico de equity curve
   - Estadísticas (win rate, drawdown, profit factor)
   - Tabla de performance por símbolo

### Fase 2: Formularios (Sesión 3)
**Estimado: 2-3 horas**

1. **TradeFormPage** (`src/pages/TradeFormPage.tsx`)
   - Formulario para crear/editar trades
   - Validación de datos
   - DatePicker para fechas
   - Selector de símbolos autocomplete

2. **Componentes de Formulario**
   - `components/Form.tsx` - Form wrapper
   - `components/FormField.tsx` - Input field con errores
   - `components/DatePicker.tsx` - Selector de fechas
   - `components/SymbolSelect.tsx` - Autocomplete de símbolos

### Fase 3: Funcionalidades Avanzadas (Sesión 4+)
**Estimado: Múltiples sesiones**

1. **CSV Importer Completo**
   - Modal con drag-drop
   - Preview de datos
   - Validación antes de importar
   - Confirmación de importación

2. **Búsqueda y Filtros**
   - Componente SearchBar
   - Filtros por símbolo, fecha, tipo
   - Ordenamiento de columnas
   - Paginación

3. **UI Polish**
   - Toast notifications
   - Modales de confirmación
   - Loading skeletons
   - Error boundaries

## 🛠️ Cómo Hacer Cambios

### Patrón para Agregar una Página Nueva

```typescript
// 1. Crear el archivo pages/MyPage.tsx
import { useMyStore } from '../store/myStore';

export function MyPage() {
  const { data, loading, error, fetchData } = useMyStore();

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className="space-y-6">
      {/* Tu contenido */}
    </div>
  );
}

// 2. Exportar en pages/index.ts
export { MyPage } from './MyPage';

// 3. Agregar ruta en App.tsx
<Route path="/mypage" element={<MyPage />} />

// 4. Agregar item en Sidebar.tsx
{ label: 'My Page', icon: 'fa-icon', href: '/mypage' }
```

### Patrón para Agregar un Servicio

```typescript
// 1. Crear services/myService.ts
import axios from 'axios';
import type { MyType } from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000/api/v1';

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const myService = {
  getAll: async () => {
    const response = await axiosInstance.get<MyType[]>('/my-endpoint');
    return response.data;
  },
  // ... más métodos
};

// 2. Crear store/myStore.ts
import { create } from 'zustand';
import type { MyType } from '../types/api';
import { myService } from '../services/myService';

interface MyStore {
  data: MyType[];
  loading: boolean;
  error: string | null;
  fetchData: () => Promise<void>;
  // ... más acciones
}

export const useMyStore = create<MyStore>((set) => ({
  data: [],
  loading: false,
  error: null,
  fetchData: async () => {
    set({ loading: true, error: null });
    try {
      const data = await myService.getAll();
      set({ data });
    } catch (error: any) {
      set({ error: error.message });
    } finally {
      set({ loading: false });
    }
  },
}));

// 3. Usar en componentes
const { data, loading } = useMyStore();
```

### Patrón para Agregar un Componente

```typescript
// 1. Crear components/MyComponent.tsx
interface MyComponentProps {
  data: string;
  onAction: (value: string) => void;
}

export function MyComponent({ data, onAction }: MyComponentProps) {
  return (
    <div className="bg-slate-800 p-4 rounded-lg">
      <p className="text-white">{data}</p>
      <button
        onClick={() => onAction('value')}
        className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
      >
        Accionar
      </button>
    </div>
  );
}

// 2. Exportar en components/index.ts si es necesario
export { MyComponent } from './MyComponent';

// 3. Usar en páginas
import { MyComponent } from '../components';

export function MyPage() {
  return <MyComponent data="test" onAction={(v) => console.log(v)} />;
}
```

## 🎨 Guía de Estilos

### Clases Tailwind Comunes

```tsx
// Contenedores
<div className="bg-slate-800 rounded-lg p-6 border border-slate-700">

// Texto
<h1 className="text-3xl font-bold text-white">
<p className="text-slate-400">

// Botones
<button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">

// Cards
<div className="grid grid-cols-4 gap-4">
  <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">

// Inputs
<input className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white" />

// Status colors
Green: text-green-400, bg-green-900/50
Red: text-red-400, bg-red-900/50
Blue: text-blue-400, bg-blue-900/50
```

## 📚 Archivos Importantes

```
front/
├── .env.local                 # Variables de ambiente
├── vite.config.ts            # Config Vite
├── tailwind.config.js         # Config Tailwind
├── tsconfig.json              # Config TypeScript
└── src/
    ├── App.tsx                # Routing principal
    ├── main.tsx               # Entry point
    ├── components/
    │   └── index.ts           # Export de componentes
    ├── pages/
    │   └── index.ts           # Export de páginas
    ├── services/              # HTTP services
    ├── store/                 # Zustand stores
    └── types/
        └── api.ts             # Tipos de API
```

## 🧪 Testing (Próximas Sesiones)

```typescript
// Ejemplo de test para un servicio
import { tradeService } from '../services/tradeService';

describe('tradeService', () => {
  it('should fetch all trades', async () => {
    const trades = await tradeService.getAll();
    expect(trades).toEqual(expect.arrayContaining([
      expect.objectContaining({ symbol: expect.any(String) })
    ]));
  });
});

// Ejemplo de test para un componente
import { render, screen } from '@testing-library/react';
import { TradesPage } from '../pages/TradesPage';

describe('TradesPage', () => {
  it('should render trades table', () => {
    render(<TradesPage />);
    expect(screen.getByText('Trading Journal')).toBeInTheDocument();
  });
});
```

## 🐛 Debugging

### Console Logging
```typescript
// En servicios
console.log('Fetching trades...', filters);

// En stores
console.log('TradeStore state:', { trades, loading, error });

// En componentes
console.log('Current props:', { data, onAction });
```

### Redux DevTools (si usas Redux)
Para Zustand: usar Zustand DevTools middleware

```typescript
import { devtools } from 'zustand/middleware';

export const useTradeStore = create<TradeStore>(
  devtools((set) => ({...}))
);
```

### React DevTools
- Instalar extensión de Chrome
- Inspeccionar props y state de componentes
- Profiler para performance

## 📝 Checklist Antes de Commit

```
- [ ] Código formateado (prettier)
- [ ] No hay console.logs de debug
- [ ] Tipos TypeScript correctos
- [ ] Sin errores en consola
- [ ] Cambios testeados manualmente
- [ ] Commit message descriptivo
- [ ] Branch actualizado con main
```

## 🚀 Deploy (Cuando esté listo)

```bash
# Build para producción
npm run build

# Preview del build
npm run preview

# Deploy a Vercel/Netlify
npm install -g vercel
vercel
```

## 📞 Preguntas Frecuentes

**P: ¿Cómo agregar un nuevo endpoint?**
R: Crear método en el servicio correspondiente, agregarle acción al store, usar en componente.

**P: ¿Cómo cambiar colores del tema?**
R: Editar `tailwind.config.js` o usar clases de Tailwind existentes.

**P: ¿Cómo manejar errores?**
R: Los stores tienen `error` state, mostrar en componentes con alert o toast.

**P: ¿Cómo agregar validación?**
R: En el componente o usar librería como `zod` o `yup`.

---

**Documentación Última**: 17 de Diciembre 2025
**Desarrollador**: AI Assistant
**Status**: Ready for Next Phase ✅

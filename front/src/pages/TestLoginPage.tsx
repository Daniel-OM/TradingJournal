import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

export const TestLoginPage = () => {
  const navigate = useNavigate();
  const { login, isAuthenticated, user, error, isLoading } = useAuthStore();
  const [status, setStatus] = useState<string>('');

  const handleTest = async () => {
    try {
      setStatus('🔄 Intentando login...');
      console.log('1. Iniciando login');
      
      await login('test', 'test123');
      
      console.log('2. Login completado');
      console.log('3. isAuthenticated:', isAuthenticated);
      console.log('4. user:', user);
      
      setStatus('✅ Login exitoso! Redirigiendo...');
      
      setTimeout(() => {
        console.log('5. Navegando a /');
        navigate('/', { replace: true });
      }, 500);
    } catch (err) {
      console.error('Error:', err);
      setStatus(`❌ Error: ${error}`);
    }
  };

  return (
    <div className="min-h-screen bg-bg text-text-primary flex items-center justify-center">
      <div className="bg-card-bg p-8 rounded-lg max-w-md w-full">
        <h1 className="text-2xl font-bold mb-4">Test Login</h1>
        
        <div className="space-y-4">
          <div className="bg-white/10 p-4 rounded text-sm">
            <p><strong>Status:</strong> {status || 'Esperando...'}</p>
            <p><strong>isLoading:</strong> {String(isLoading)}</p>
            <p><strong>isAuthenticated:</strong> {String(isAuthenticated)}</p>
            <p><strong>user:</strong> {user ? user.username : 'null'}</p>
            <p><strong>error:</strong> {error || 'null'}</p>
          </div>
          
          <button
            onClick={handleTest}
            disabled={isLoading}
            className="w-full bg-primary text-white py-2 rounded-pill font-semibold hover:opacity-90 disabled:opacity-50"
          >
            {isLoading ? 'Cargando...' : 'Test Login (test/test123)'}
          </button>
          
          <button
            onClick={() => {
              console.log('Store state:', { isAuthenticated, user });
              navigate('/', { replace: true });
            }}
            className="w-full bg-secondary text-white py-2 rounded-pill font-semibold hover:opacity-90"
          >
            Ir a Home Manualmente
          </button>
        </div>
        
        <div className="mt-6 bg-yellow-900/30 border border-warning p-4 rounded text-sm">
          <p>Abre la consola (F12) para ver los logs detallados</p>
        </div>
      </div>
    </div>
  );
};

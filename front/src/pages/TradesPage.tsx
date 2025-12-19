import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTradeStore } from '../store/tradeStore';

export function TradesPage() {
  const navigate = useNavigate();
  const { trades, loading, error, fetchTrades, deleteTrade } = useTradeStore();
  const [currentMonth, setCurrentMonth] = useState(new Date());

  useEffect(() => {
    const year = currentMonth.getFullYear();
    const month = currentMonth.getMonth() + 1;
    fetchTrades({
      date_from: `${year}-${String(month).padStart(2, '0')}-01`,
      date_to: `${year}-${String(month).padStart(2, '0')}-31`,
    });
  }, [currentMonth, fetchTrades]);

  const handlePrevMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1));
  };

  const handleNextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1));
  };

  const handleDeleteTrade = async (tradeId: string) => {
    if (confirm('¿Estás seguro de que quieres eliminar este trade?')) {
      try {
        await deleteTrade(tradeId);
      } catch (err) {
        console.error('Error deleting trade:', err);
      }
    }
  };

  if (error) {
    return (
      <div className="text-red-500 p-4 bg-red-900/20 rounded-lg">
        Error: {error}
      </div>
    );
  }

  const monthName = currentMonth.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' });
  const totalPnL = trades.reduce((sum, t) => sum + (t.profit_loss || t.pnl || 0), 0);
  const winningTrades = trades.filter((t) => (t.profit_loss || t.pnl || 0) > 0).length;
  const winRate = trades.length > 0 ? ((winningTrades / trades.length) * 100).toFixed(1) : '0';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Trading Journal</h1>
          <p className="text-slate-400 mt-1">Registro de todos tus trades</p>
        </div>
        <button
          onClick={() => navigate('/trades/new')}
          className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium flex items-center gap-2 transition-colors"
        >
          <i className="fas fa-plus"></i>
          Nuevo Trade
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
          <p className="text-slate-400 text-sm">Total Trades</p>
          <p className="text-2xl font-bold text-white mt-2">{trades.length}</p>
        </div>
        <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
          <p className="text-slate-400 text-sm">Win Rate</p>
          <p className="text-2xl font-bold text-white mt-2">{winRate}%</p>
        </div>
        <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
          <p className="text-slate-400 text-sm">Monthly P&L</p>
          <p className={`text-2xl font-bold mt-2 ${totalPnL >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            ${totalPnL.toFixed(2)}
          </p>
        </div>
        <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
          <p className="text-slate-400 text-sm">Avg Win</p>
          <p className="text-2xl font-bold text-white mt-2">
            $
            {winningTrades > 0
              ? (trades.filter((t) => (t.profit_loss || t.pnl || 0) > 0).reduce((s, t) => s + (t.profit_loss || t.pnl || 0), 0) / winningTrades).toFixed(2)
              : '0'}
          </p>
        </div>
      </div>

      {/* Month Navigation */}
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <div className="flex items-center justify-between mb-6">
          <button onClick={handlePrevMonth} className="p-2 hover:bg-slate-700 rounded-lg transition-colors">
            <i className="fas fa-chevron-left text-white"></i>
          </button>
          <h2 className="text-2xl font-bold text-white capitalize">{monthName}</h2>
          <button onClick={handleNextMonth} className="p-2 hover:bg-slate-700 rounded-lg transition-colors">
            <i className="fas fa-chevron-right text-white"></i>
          </button>
        </div>

        {/* Trades Table */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          </div>
        ) : trades.length === 0 ? (
          <div className="text-center py-12 text-slate-400">
            <i className="fas fa-inbox text-4xl mb-4"></i>
            <p>No hay trades en este mes</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="px-4 py-3 text-left text-slate-300 font-medium">Símbolo</th>
                  <th className="px-4 py-3 text-left text-slate-300 font-medium">Tipo</th>
                  <th className="px-4 py-3 text-left text-slate-300 font-medium">Entrada</th>
                  <th className="px-4 py-3 text-left text-slate-300 font-medium">Salida</th>
                  <th className="px-4 py-3 text-left text-slate-300 font-medium">Cantidad</th>
                  <th className="px-4 py-3 text-left text-slate-300 font-medium">P&L</th>
                  <th className="px-4 py-3 text-left text-slate-300 font-medium">%</th>
                  <th className="px-4 py-3 text-left text-slate-300 font-medium">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {trades.map((trade) => (
                  <tr key={trade.id} className="border-b border-slate-700 hover:bg-slate-700/50 transition-colors">
                    <td className="px-4 py-3 text-white font-medium">{trade.symbol}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`px-2 py-1 rounded text-sm font-medium ${
                          trade.trade_type === 'LONG'
                            ? 'bg-green-900/50 text-green-300'
                            : 'bg-red-900/50 text-red-300'
                        }`}
                      >
                        {trade.trade_type}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-300">${trade.entry_price.toFixed(2)}</td>
                    <td className="px-4 py-3 text-slate-300">${(trade.exit_price || 0).toFixed(2)}</td>
                    <td className="px-4 py-3 text-slate-300">{trade.quantity}</td>
                    <td className={`px-4 py-3 font-medium ${(trade.profit_loss || trade.pnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      ${(trade.profit_loss || trade.pnl || 0).toFixed(2)}
                    </td>
                    <td className={`px-4 py-3 font-medium ${(trade.profit_loss || trade.pnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {(trade.entry_price && trade.exit_price) ? ((trade.exit_price - trade.entry_price) / trade.entry_price * 100).toFixed(2) : '0'}%
                    </td>
                    <td className="px-4 py-3 space-x-2 flex">
                      <button
                        onClick={() => navigate(`/trades/${trade.id}`)}
                        className="p-2 text-blue-400 hover:bg-slate-600 rounded transition-colors"
                        title="Ver detalles"
                      >
                        <i className="fas fa-eye"></i>
                      </button>
                      <button
                        onClick={() => navigate(`/trades/${trade.id}/edit`)}
                        className="p-2 text-yellow-400 hover:bg-slate-600 rounded transition-colors"
                        title="Editar"
                      >
                        <i className="fas fa-edit"></i>
                      </button>
                      <button
                        onClick={() => handleDeleteTrade(trade.id)}
                        className="p-2 text-red-400 hover:bg-slate-600 rounded transition-colors"
                        title="Eliminar"
                      >
                        <i className="fas fa-trash"></i>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Import Trades */}
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h3 className="text-lg font-bold text-white mb-4">Importar Trades</h3>
        <div className="border-2 border-dashed border-slate-600 rounded-lg p-8 text-center hover:border-blue-500 transition-colors cursor-pointer">
          <i className="fas fa-upload text-slate-400 text-3xl mb-3"></i>
          <p className="text-slate-400">Arrastra archivos CSV aquí o haz clic para seleccionar</p>
          <p className="text-slate-500 text-sm mt-1">Formatos soportados: CSV</p>
        </div>
      </div>
    </div>
  );
}

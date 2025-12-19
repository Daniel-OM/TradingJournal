import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTradeStore } from '../store/tradeStore';

export function TradeDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { currentTrade, loading, error, fetchTrade, deleteTrade } = useTradeStore();
  const [isConfirmingDelete, setIsConfirmingDelete] = useState(false);

  useEffect(() => {
    if (id) {
      fetchTrade(id);
    }
  }, [id, fetchTrade]);

  const handleDelete = async () => {
    if (currentTrade && id) {
      try {
        await deleteTrade(id);
        navigate('/trades');
      } catch (err) {
        console.error('Error deleting trade:', err);
        setIsConfirmingDelete(false);
      }
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error || !currentTrade) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/trades')}
            className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
          >
            <i className="fas fa-arrow-left text-white"></i>
          </button>
          <h1 className="text-2xl font-bold text-white">Trade Not Found</h1>
        </div>
        <div className="text-red-500 p-4 bg-red-900/20 rounded-lg">
          {error || 'Trade not found'}
        </div>
      </div>
    );
  }

  const pnlValue = currentTrade.profit_loss || currentTrade.pnl || 0;
  const pnlPercentage = currentTrade.entry_price && currentTrade.exit_price
    ? ((currentTrade.exit_price - currentTrade.entry_price) / currentTrade.entry_price * 100).toFixed(2)
    : '0';

  const isProfitable = pnlValue >= 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/trades')}
            className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
          >
            <i className="fas fa-arrow-left text-white"></i>
          </button>
          <div>
            <h1 className="text-3xl font-bold text-white">{currentTrade.symbol}</h1>
            <p className="text-slate-400 mt-1">
              {currentTrade.trade_type === 'LONG' ? '🟢 Long' : '🔴 Short'} • 
              {new Date(currentTrade.entry_date).toLocaleDateString('es-ES')}
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => navigate(`/trades/${id}/edit`)}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium flex items-center gap-2 transition-colors"
          >
            <i className="fas fa-edit"></i>
            Edit
          </button>
          <button
            onClick={() => setIsConfirmingDelete(true)}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium flex items-center gap-2 transition-colors"
          >
            <i className="fas fa-trash"></i>
            Delete
          </button>
        </div>
      </div>

      {/* Confirmation Modal */}
      {isConfirmingDelete && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-lg p-6 max-w-md border border-slate-700">
            <h2 className="text-xl font-bold text-white mb-4">Confirm Deletion</h2>
            <p className="text-slate-300 mb-6">
              Are you sure you want to delete this trade? This action cannot be undone.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setIsConfirmingDelete(false)}
                className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-colors"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Grid */}
      <div className="grid grid-cols-3 gap-6">
        {/* Left Column - Trade Details */}
        <div className="col-span-2 space-y-6">
          {/* Trade Summary */}
          <div className="grid grid-cols-2 gap-4">
            {/* Entry Details */}
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h3 className="text-sm font-semibold text-slate-400 uppercase mb-4">Entry</h3>
              <div className="space-y-4">
                <div>
                  <p className="text-slate-500 text-xs">Date</p>
                  <p className="text-white font-semibold">
                    {new Date(currentTrade.entry_date).toLocaleDateString('es-ES')}
                  </p>
                </div>
                <div>
                  <p className="text-slate-500 text-xs">Price</p>
                  <p className="text-white font-semibold">${currentTrade.entry_price.toFixed(2)}</p>
                </div>
              </div>
            </div>

            {/* Exit Details */}
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h3 className="text-sm font-semibold text-slate-400 uppercase mb-4">Exit</h3>
              <div className="space-y-4">
                <div>
                  <p className="text-slate-500 text-xs">Date</p>
                  <p className="text-white font-semibold">
                    {currentTrade.exit_date
                      ? new Date(currentTrade.exit_date).toLocaleDateString('es-ES')
                      : 'Still open'}
                  </p>
                </div>
                <div>
                  <p className="text-slate-500 text-xs">Price</p>
                  <p className="text-white font-semibold">${(currentTrade.exit_price || 0).toFixed(2)}</p>
                </div>
              </div>
            </div>

            {/* Quantity & Type */}
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h3 className="text-sm font-semibold text-slate-400 uppercase mb-4">Position</h3>
              <div className="space-y-4">
                <div>
                  <p className="text-slate-500 text-xs">Quantity</p>
                  <p className="text-white font-semibold">{currentTrade.quantity}</p>
                </div>
                <div>
                  <p className="text-slate-500 text-xs">Type</p>
                  <p className={`font-semibold ${currentTrade.trade_type === 'LONG' ? 'text-green-400' : 'text-red-400'}`}>
                    {currentTrade.trade_type}
                  </p>
                </div>
              </div>
            </div>

            {/* Commissions & Fees */}
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h3 className="text-sm font-semibold text-slate-400 uppercase mb-4">Fees</h3>
              <div className="space-y-4">
                <div>
                  <p className="text-slate-500 text-xs">Commission</p>
                  <p className="text-white font-semibold">${(currentTrade.commission || 0).toFixed(2)}</p>
                </div>
                {currentTrade.stop_loss && (
                  <div>
                    <p className="text-slate-500 text-xs">Stop Loss</p>
                    <p className="text-white font-semibold">${currentTrade.stop_loss.toFixed(2)}</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Strategy & Notes */}
          {currentTrade.strategy_id && (
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h3 className="text-sm font-semibold text-slate-400 uppercase mb-4">Strategy</h3>
              <p className="text-white">Strategy ID: {currentTrade.strategy_id}</p>
            </div>
          )}

          {currentTrade.notes && (
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h3 className="text-sm font-semibold text-slate-400 uppercase mb-4">Notes</h3>
              <p className="text-slate-300 whitespace-pre-wrap">{currentTrade.notes}</p>
            </div>
          )}
        </div>

        {/* Right Column - P&L Summary */}
        <div className="space-y-4">
          {/* P&L Card */}
          <div className={`rounded-lg p-6 border ${isProfitable ? 'bg-green-900/30 border-green-700' : 'bg-red-900/30 border-red-700'}`}>
            <p className="text-slate-400 text-sm">Profit & Loss</p>
            <p className={`text-4xl font-bold mt-2 ${isProfitable ? 'text-green-400' : 'text-red-400'}`}>
              ${(currentTrade.profit_loss || currentTrade.pnl || 0).toFixed(2)}
            </p>
            <p className={`text-sm mt-2 ${isProfitable ? 'text-green-400' : 'text-red-400'}`}>
              {isProfitable ? '+' : ''}{pnlPercentage}%
            </p>
          </div>

          {/* Trade Duration */}
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
            <p className="text-slate-400 text-sm">Duration</p>
            <p className="text-2xl font-bold text-white mt-2">
              {currentTrade.exit_date
                ? `${Math.ceil(
                    (new Date(currentTrade.exit_date).getTime() - new Date(currentTrade.entry_date).getTime()) /
                      (1000 * 60 * 60 * 24)
                  )} days`
                : 'Open'}
            </p>
          </div>

          {/* Tags/Hashtags */}
          {currentTrade.hashtags && (
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <p className="text-slate-400 text-sm mb-3">Tags</p>
              <div className="flex flex-wrap gap-2">
                {currentTrade.hashtags.split(',').map((tag: string, idx: number) => (
                  <span
                    key={idx}
                    className="px-3 py-1 bg-blue-900/50 border border-blue-600 text-blue-300 text-xs rounded-full"
                  >
                    {tag.trim()}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTradeStore } from '../store/tradeStore';
import { useStrategyStore } from '../store/strategyStore';
import type { TradeCreate } from '../types/api';

export function TradeFormPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { currentTrade, createTrade, updateTrade, fetchTrade } = useTradeStore();
  const { strategies, fetchStrategies } = useStrategyStore();
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const [formData, setFormData] = useState<TradeCreate>({
    symbol: '',
    trade_type: 'LONG',
    entry_date: new Date().toISOString().split('T')[0],
    entry_price: 0,
    exit_price: undefined,
    quantity: 0,
    commission: 0,
    notes: '',
    hashtags: '',
  });

  useEffect(() => {
    fetchStrategies();
    
    if (id) {
      fetchTrade(id);
    }
  }, [id, fetchStrategies, fetchTrade]);

  useEffect(() => {
    if (id && currentTrade) {
      setFormData({
        symbol: currentTrade.symbol,
        company_name: currentTrade.company_name,
        trade_type: currentTrade.trade_type,
        entry_date: currentTrade.entry_date.split('T')[0],
        entry_time: currentTrade.entry_time,
        entry_price: currentTrade.entry_price,
        exit_date: currentTrade.exit_date ? currentTrade.exit_date.split('T')[0] : undefined,
        exit_time: currentTrade.exit_time,
        exit_price: currentTrade.exit_price,
        exit_quantity: currentTrade.exit_quantity,
        quantity: currentTrade.quantity,
        commission: currentTrade.commission || 0,
        notes: currentTrade.notes || '',
        hashtags: currentTrade.hashtags || '',
        strategy_id: currentTrade.strategy_id,
        balance: currentTrade.balance,
        description: currentTrade.description,
        why_profitable: currentTrade.why_profitable,
        influencing_factors: currentTrade.influencing_factors,
        stop_loss: currentTrade.stop_loss,
        take_profit: currentTrade.take_profit,
      });
    }
  }, [currentTrade, id]);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.symbol || formData.symbol.trim() === '') {
      newErrors.symbol = 'Symbol is required';
    }
    if (formData.entry_price <= 0) {
      newErrors.entry_price = 'Entry price must be greater than 0';
    }
    if (formData.exit_price && formData.exit_price <= 0) {
      newErrors.exit_price = 'Exit price must be greater than 0';
    }
    if (formData.quantity <= 0) {
      newErrors.quantity = 'Quantity must be greater than 0';
    }
    if (!formData.entry_date) {
      newErrors.entry_date = 'Entry date is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      if (id && currentTrade) {
        await updateTrade(id, formData);
        navigate(`/trades/${id}`);
      } else {
        const result = await createTrade(formData);
        navigate(`/trades/${result.id}`);
      }
    } catch (error) {
      console.error('Error saving trade:', error);
      setErrors({ submit: 'Failed to save trade. Please try again.' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    if (id) {
      navigate(`/trades/${id}`);
    } else {
      navigate('/trades');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">
            {id ? 'Edit Trade' : 'New Trade'}
          </h1>
          <p className="text-slate-400 mt-1">
            {id ? 'Update trade details' : 'Create a new trade entry'}
          </p>
        </div>
      </div>

      {/* Error Message */}
      {errors.submit && (
        <div className="p-4 bg-red-900/20 border border-red-700 rounded-lg text-red-400">
          {errors.submit}
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="bg-slate-800 rounded-lg p-8 border border-slate-700">
        <div className="grid grid-cols-2 gap-6">
          {/* Symbol */}
          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-2">
              Symbol *
            </label>
            <input
              type="text"
              value={formData.symbol}
              onChange={(e) => {
                setFormData({ ...formData, symbol: e.target.value.toUpperCase() });
                if (errors.symbol) setErrors({ ...errors, symbol: '' });
              }}
              placeholder="e.g., AAPL"
              className={`w-full px-4 py-2 bg-slate-900 border rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 ${
                errors.symbol ? 'border-red-500' : 'border-slate-600'
              }`}
            />
            {errors.symbol && <p className="text-red-400 text-sm mt-1">{errors.symbol}</p>}
          </div>

          {/* Trade Type */}
          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-2">
              Trade Type *
            </label>
            <select
              value={formData.trade_type}
              onChange={(e) => setFormData({ ...formData, trade_type: e.target.value as 'LONG' | 'SHORT' })}
              className="w-full px-4 py-2 bg-slate-900 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
            >
              <option value="LONG">Long</option>
              <option value="SHORT">Short</option>
            </select>
          </div>

          {/* Entry Date */}
          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-2">
              Entry Date *
            </label>
            <input
              type="date"
              value={formData.entry_date}
              onChange={(e) => {
                setFormData({ ...formData, entry_date: e.target.value });
                if (errors.entry_date) setErrors({ ...errors, entry_date: '' });
              }}
              className={`w-full px-4 py-2 bg-slate-900 border rounded-lg text-white focus:outline-none focus:border-blue-500 ${
                errors.entry_date ? 'border-red-500' : 'border-slate-600'
              }`}
            />
            {errors.entry_date && <p className="text-red-400 text-sm mt-1">{errors.entry_date}</p>}
          </div>

          {/* Entry Price */}
          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-2">
              Entry Price *
            </label>
            <input
              type="number"
              step="0.01"
              value={formData.entry_price}
              onChange={(e) => {
                setFormData({ ...formData, entry_price: parseFloat(e.target.value) });
                if (errors.entry_price) setErrors({ ...errors, entry_price: '' });
              }}
              className={`w-full px-4 py-2 bg-slate-900 border rounded-lg text-white focus:outline-none focus:border-blue-500 ${
                errors.entry_price ? 'border-red-500' : 'border-slate-600'
              }`}
            />
            {errors.entry_price && <p className="text-red-400 text-sm mt-1">{errors.entry_price}</p>}
          </div>

          {/* Exit Date */}
          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-2">
              Exit Date (Optional)
            </label>
            <input
              type="date"
              value={formData.exit_date || ''}
              onChange={(e) => setFormData({ ...formData, exit_date: e.target.value || undefined })}
              className="w-full px-4 py-2 bg-slate-900 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* Exit Price */}
          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-2">
              Exit Price *
            </label>
            <input
              type="number"
              step="0.01"
              value={formData.exit_price}
              onChange={(e) => {
                setFormData({ ...formData, exit_price: parseFloat(e.target.value) });
                if (errors.exit_price) setErrors({ ...errors, exit_price: '' });
              }}
              className={`w-full px-4 py-2 bg-slate-900 border rounded-lg text-white focus:outline-none focus:border-blue-500 ${
                errors.exit_price ? 'border-red-500' : 'border-slate-600'
              }`}
            />
            {errors.exit_price && <p className="text-red-400 text-sm mt-1">{errors.exit_price}</p>}
          </div>

          {/* Quantity */}
          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-2">
              Quantity *
            </label>
            <input
              type="number"
              step="1"
              value={formData.quantity}
              onChange={(e) => {
                setFormData({ ...formData, quantity: parseFloat(e.target.value) });
                if (errors.quantity) setErrors({ ...errors, quantity: '' });
              }}
              className={`w-full px-4 py-2 bg-slate-900 border rounded-lg text-white focus:outline-none focus:border-blue-500 ${
                errors.quantity ? 'border-red-500' : 'border-slate-600'
              }`}
            />
            {errors.quantity && <p className="text-red-400 text-sm mt-1">{errors.quantity}</p>}
          </div>

          {/* Commission */}
          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-2">
              Commission (Optional)
            </label>
            <input
              type="number"
              step="0.01"
              value={formData.commission || 0}
              onChange={(e) => setFormData({ ...formData, commission: parseFloat(e.target.value) })}
              className="w-full px-4 py-2 bg-slate-900 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* Stop Loss */}
          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-2">
              Stop Loss (Optional)
            </label>
            <input
              type="number"
              step="0.01"
              value={formData.stop_loss || ''}
              onChange={(e) => setFormData({ ...formData, stop_loss: e.target.value ? parseFloat(e.target.value) : undefined })}
              className="w-full px-4 py-2 bg-slate-900 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* Strategy */}
          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-2">
              Strategy (Optional)
            </label>
            <select
              value={formData.strategy_id || ''}
              onChange={(e) => setFormData({ ...formData, strategy_id: e.target.value || undefined })}
              className="w-full px-4 py-2 bg-slate-900 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
            >
              <option value="">No Strategy</option>
              {strategies.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>

          {/* Hashtags */}
          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-2">
              Tags (Optional)
            </label>
            <input
              type="text"
              value={formData.hashtags || ''}
              onChange={(e) => setFormData({ ...formData, hashtags: e.target.value })}
              placeholder="e.g., breakout, reversal (comma-separated)"
              className="w-full px-4 py-2 bg-slate-900 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>

        {/* Notes */}
        <div className="mt-6">
          <label className="block text-sm font-semibold text-slate-300 mb-2">
            Notes (Optional)
          </label>
          <textarea
            value={formData.notes || ''}
            onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
            placeholder="Trade analysis, setup description, etc."
            rows={5}
            className="w-full px-4 py-2 bg-slate-900 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </div>

        {/* Buttons */}
        <div className="flex gap-3 mt-8 pt-6 border-t border-slate-600">
          <button
            type="button"
            onClick={handleCancel}
            disabled={isLoading}
            className="flex-1 px-6 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isLoading}
            className="flex-1 px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                {id ? 'Updating...' : 'Creating...'}
              </>
            ) : (
              <>{id ? 'Update Trade' : 'Create Trade'}</>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}

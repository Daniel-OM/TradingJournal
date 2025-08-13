
from datetime import datetime
import numpy as np
from ..models.trade import Trade

class PerformanceMetrics:

    def __init__(self, trades:list[Trade]):
        self.trades = trades


    def _normal_cdf(self, x):
        """Aproximación de la función de distribución acumulativa normal estándar"""
        # Aproximación de Abramowitz y Stegun
        if x < 0:
            return 1 - self._normal_cdf(-x)
        
        # Constantes
        a1 =  0.254829592
        a2 = -0.284496736
        a3 =  1.421413741
        a4 = -1.453152027
        a5 =  1.061405429
        p  =  0.3275911
        
        t = 1.0 / (1.0 + p * x)
        y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * np.exp(-x * x)
        
        return y

    def _t_test_p_value_approx(self, t_stat, df):
        """Aproximación del p-value para distribución t"""
        # Para grados de libertad pequeños, usamos aproximaciones
        if df >= 30:
            return 2 * (1 - self._normal_cdf(t_stat))
        
        # Tabla de valores críticos t aproximados para p-value de dos colas
        critical_values = {
            1: [12.706, 63.657, 636.619],     # p: 0.1, 0.02, 0.002
            2: [4.303, 9.925, 31.599],
            3: [3.182, 5.841, 12.924],
            4: [2.776, 4.604, 8.610],
            5: [2.571, 4.032, 6.869],
            10: [2.228, 3.169, 4.587],
            15: [2.131, 2.947, 4.073],
            20: [2.086, 2.845, 3.850],
            25: [2.060, 2.787, 3.725],
            29: [2.045, 2.756, 3.659]
        }
        
        # Encontrar el df más cercano en nuestra tabla
        closest_df = min(critical_values.keys(), key=lambda x: abs(x - df))
        t_values = critical_values[closest_df]
        
        if t_stat >= t_values[2]:      # p < 0.002
            return 0.001
        elif t_stat >= t_values[1]:    # p < 0.02
            return 0.01
        elif t_stat >= t_values[0]:    # p < 0.1
            return 0.05
        else:
            return 0.2  # p > 0.1
        
    def calculatePvalue(self, pnl_values:list, method:str='custom'):
        
        try:
            if method == 'scipy':
                from scipy import stats
                t_stat, p_value = stats.ttest_1samp(pnl_values, 0)
                p_value = p_value if not np.isnan(p_value) else 1.0
            else:
                n = len(pnl_values)
                mean_pnl = np.mean(pnl_values)
                std_pnl = np.std(pnl_values, ddof=1)  # Sample standard deviation
                
                if std_pnl == 0 or n <= 1:
                    p_value = 1.0
                else:
                    # Calcular t-statistic
                    t_stat = mean_pnl / (std_pnl / np.sqrt(n))
                    
                    # Aproximación del p-value usando distribución normal para n > 30
                    # Para n <= 30, usamos una aproximación conservadora
                    if n > 30:
                        # Para muestras grandes, t se aproxima a normal estándar
                        p_value = 2 * (1 - self._normal_cdf(abs(t_stat)))
                    else:
                        # Para muestras pequeñas, usamos tabla t aproximada
                        p_value = self._t_test_p_value_approx(abs(t_stat), n - 1)
                        
                p_value = min(max(p_value, 0.0), 1.0)  # Asegurar que esté en [0,1]
            
            return p_value
        
        except Exception as e:
            print('Error trying to calculate p-value: ', e)
            return 1.0

    def calculateMaxDrawDown(self, pnl_values:list[float]):
        """Calcular máximo drawdown"""
        if not pnl_values:
            return 0
        
        cumulative_pnl = 0
        peak = 0
        max_dd = 0
        
        for pnl in pnl_values:
            cumulative_pnl += pnl
            if cumulative_pnl > peak:
                peak = cumulative_pnl
            drawdown = peak - cumulative_pnl
            if drawdown > max_dd:
                max_dd = drawdown
        
        return max_dd
    
    def calculateAdvancedStats(self, pnl_values:list[float]):
        """Calcular estadísticas avanzadas (Gold)"""
        if not pnl_values or len(pnl_values) < 2:
            return {'sqn': 0, 'k_ratio': 0, 'kelly_percent': 0, 'p_value': 1.0}
        
        # SQN (System Quality Number)
        avg_pnl = np.mean(pnl_values)
        std_pnl = np.std(pnl_values)
        sqn = (avg_pnl / std_pnl) * np.sqrt(len(pnl_values)) if std_pnl != 0 else 0
        
        # K-Ratio (simplificado)
        cumulative_pnl = np.cumsum(pnl_values)
        if len(cumulative_pnl) > 1:
            slope = np.polyfit(range(len(cumulative_pnl)), cumulative_pnl, 1)[0]
            residuals = cumulative_pnl - np.polyval([slope, 0], range(len(cumulative_pnl)))
            std_residuals = np.std(residuals)
            k_ratio = slope / std_residuals if std_residuals != 0 else 0
        else:
            k_ratio = 0
        
        # Kelly % (simplificado)
        win_rate = len([p for p in pnl_values if p > 0]) / len(pnl_values)
        if win_rate > 0 and win_rate < 1:
            avg_win = np.mean([p for p in pnl_values if p > 0])
            avg_loss = abs(np.mean([p for p in pnl_values if p < 0])) if any(p < 0 for p in pnl_values) else 1
            kelly_percent = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win * 100
        else:
            kelly_percent = 0
        
        # P-value (t-test simple)
        p_value = self.calculatePvalue(pnl_values=pnl_values, method='custom')
        
        return {
            'sqn': sqn,
            'k_ratio': k_ratio,
            'kelly_percent': kelly_percent,
            'p_value': p_value
        }

    def calculateStreaks(self, pnl_values:list[float]):
        """Calcular rachas consecutivas máximas"""
        if not pnl_values:
            return {'max_wins': 0, 'max_losses': 0}
        
        max_wins = 0
        max_losses = 0
        current_wins = 0
        current_losses = 0
        
        for pnl in pnl_values:
            if pnl > 0:
                current_wins += 1
                current_losses = 0
                max_wins = max(max_wins, current_wins)
            elif pnl < 0:
                current_losses += 1
                current_wins = 0
                max_losses = max(max_losses, current_losses)
            else:  # scratch
                current_wins = 0
                current_losses = 0
        
        return {'max_wins': max_wins, 'max_losses': max_losses}

    def calculateDailyStats(self, mode:str='net'):
        """Calcular estadísticas diarias"""
        
        # Determinar rango de fechas
        start_date = min((trade.entry_date for trade in self.trades if trade.entry_date), default=None)
        end_date = max((trade.entry_date for trade in self.trades if trade.entry_date), default=None)

        if start_date and end_date:
            trading_days = (end_date - start_date).days + 1
        else:
            first_trade = min(self.trades, key=lambda t: t.entry_date)
            last_trade = max(self.trades, key=lambda t: t.entry_date)
            trading_days = (last_trade.entry_date - first_trade.entry_date).days + 1
        
        if trading_days == 0:
            trading_days = 1
        
        total_pnl = sum((trade.profit_loss + trade.commission if mode == 'gross' else trade.profit_loss) for trade in self.trades)
        total_volume = sum(getattr(trade, 'exit_quantity', 0) for trade in self.trades)
        
        return {
            'avg_daily_pnl': total_pnl / trading_days,
            'avg_daily_volume': total_volume / trading_days
        }

    def getStats(self, mode='net'):

        pnl_values = [(trade.profit_loss + trade.commission) if mode == 'gross' else trade.profit_loss for trade in self.trades]

        total_pnl = sum(pnl_values)
        total_quantity = sum([trade.exit_quantity for trade in self.trades if hasattr(trade, 'exit_quantity')])
        winning_trades = len([p for p in pnl_values if p > 0])
        losing_trades = len([p for p in pnl_values if p < 0])
        scratch_trades = len([p for p in pnl_values if p == 0])
        total_trades = len(pnl_values)
        
        winning_pnl = [p for p in pnl_values if p > 0]
        losing_pnl = [p for p in pnl_values if p < 0]
        
        avg_trade_pnl = np.mean(pnl_values) if pnl_values else 0
        avg_pnl_per_share = total_pnl / total_quantity if total_quantity != 0 else 0
        median_trade_pnl = np.median(pnl_values) if pnl_values else 0
        avg_win = np.mean(winning_pnl) if winning_pnl else 0
        avg_loss = np.mean(losing_pnl) if losing_pnl else 0
        
        largest_gain = max(pnl_values) if pnl_values else 0
        largest_loss = min(pnl_values) if pnl_values else 0
        
        # Risk/Reward y Profit Factor
        risk_reward = avg_win / abs(avg_loss) if avg_loss != 0 else 0
        
        total_wins = sum(winning_pnl) if winning_pnl else 0
        total_losses = abs(sum(losing_pnl)) if losing_pnl else 0
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf') if total_wins > 0 else 0
        
        # Desviación estándar
        trade_pnl_std = np.std(pnl_values) if len(pnl_values) > 1 else 0
        
        # Sharpe Ratio
        sharpe_ratio = (avg_trade_pnl / trade_pnl_std) if trade_pnl_std != 0 else 0
        
        # Maximum Drawdown
        max_drawdown = self.calculateMaxDrawDown(pnl_values=pnl_values)
        
        advanced_stats = self.calculateAdvancedStats(pnl_values=pnl_values)

        # ===== RACHAS CONSECUTIVAS =====
        consecutive_stats = self.calculateStreaks(pnl_values=pnl_values)
        
        # ===== ESTADÍSTICAS TEMPORALES =====
        daily_stats = self.calculateDailyStats(mode=mode)
        
        return {
            'total_pnl': total_pnl,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'scratch_trades': scratch_trades,
            'win_rate': (winning_trades / total_trades * 100) if total_trades > 0 else 0,
            'loss_rate': (losing_trades / total_trades * 100) if total_trades > 0 else 0,
            'winning_pnl': sum(winning_pnl),
            'losing_pnl': sum(losing_pnl),
            'avg_trade_pnl': avg_trade_pnl,
            'avg_pnl_per_share': round(avg_pnl_per_share, 4),
            'median_trade_pnl': median_trade_pnl,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'largest_gain': largest_gain,
            'largest_loss': largest_loss,
            'risk_reward': risk_reward,
            'total_wins': total_wins,
            'total_losses': total_losses,
            'profit_factor': profit_factor,
            'trade_pnl_std': trade_pnl_std,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,

            'sqn': round(advanced_stats['sqn'], 2),
            'k_ratio': round(advanced_stats['k_ratio'], 2),
            'kelly_percent': round(advanced_stats['kelly_percent'], 2),
            'p_value': round(advanced_stats['p_value'], 4),
            
            # Rachas
            'max_consecutive_wins': consecutive_stats['max_wins'],
            'max_consecutive_losses': consecutive_stats['max_losses'],

            'avg_daily_pnl': round(daily_stats['avg_daily_pnl'], 2),
            'avg_daily_volume': round(daily_stats['avg_daily_volume'], 2),
        }

    def _formatHoldTime(self, minutes):
        if minutes < 60:
            return f"{int(minutes)}m"
        elif minutes < 1440:  # Menos de 24 horas (24 * 60 = 1440 minutos)
            hours = minutes // 60
            mins = minutes % 60
            if mins == 0:
                return f"{int(hours)}h"
            else:
                return f"{int(hours)}h {int(mins)}m"
        else:  # 1440 minutos o más (1+ días)
            days = minutes // 1440
            remaining_minutes = minutes % 1440
            hours = remaining_minutes // 60
            mins = remaining_minutes % 60
            
            result = f"{int(days)}d"
            if hours > 0:
                result += f" {int(hours)}h"
            if mins > 0:
                result += f" {int(mins)}m"
            return result
            
    def calculateHoldTimes(self):
        """Calcular tiempos de mantenimiento promedio"""
        def get_hold_time(trade:Trade):
            if hasattr(trade, 'exit_date') and trade.exit_date and trade.entry_date:
                if hasattr(trade, 'entry_time') and hasattr(trade, 'exit_time'):
                    entry_datetime = datetime.combine(trade.entry_date, datetime.strptime(trade.entry_time, '%H:%M:%S').time() or datetime.min.time())
                    exit_datetime = datetime.combine(trade.exit_date, datetime.strptime(trade.exit_time, '%H:%M:%S').time() or datetime.min.time())
                    return (exit_datetime - entry_datetime).total_seconds() / 60
                else:
                    return (trade.exit_date - trade.entry_date).days * 24 * 60
            return 0
        
        hold_times_all = []
        hold_times_winners = []
        hold_times_losers = []
        hold_times_scratches = []
        
        for trade in self.trades:
            hold_time = get_hold_time(trade)
            hold_times_all.append(hold_time)
            
            if trade.profit_loss > 0:
                hold_times_winners.append(hold_time)
            elif trade.profit_loss < 0:
                hold_times_losers.append(hold_time)
            else:
                hold_times_scratches.append(hold_time)
        
        return {
            'overall': self._formatHoldTime(np.mean(hold_times_all)) if hold_times_all else "0h",
            'winners': self._formatHoldTime(np.mean(hold_times_winners)) if hold_times_winners else "0h",
            'losers': self._formatHoldTime(np.mean(hold_times_losers)) if hold_times_losers else "0h",
            'scratches': self._formatHoldTime(np.mean(hold_times_scratches)) if hold_times_scratches else "0h",
        }

    def calculateMaximumExecutions(self):
        """Calcular Maximum Favorable/Adverse Excursion"""
        mfe_values = []
        mae_values = []
        
        for trade in self.trades:
            mae, mfe = trade.maximumFavorableAverse()
            mfe_values.append(mfe)
            mae_values.append(mae)
        
        return {
            'avg_mfe': np.mean(mfe_values) if mfe_values else 0,
            'avg_mae': np.mean(mae_values) if mae_values else 0
        }

    def getEmpty():

        return {
            'total_pnl': 0, 'avg_daily_pnl': 0, 'avg_daily_volume': 0, 'avg_trade_pnl': 0,
            'median_trade_pnl': 0, 'total_trades': 0, 'winning_trades': 0, 'losing_trades': 0,
            'scratch_trades': 0, 'win_rate': 0, 'loss_rate': 0, 'largest_gain': 0, 'largest_loss': 0,
            'max_consecutive_wins': 0, 'max_consecutive_losses': 0, 'per_share_avg_pnl': 0,
            'trade_pnl_std': 0, 'profit_factor': 0, 'risk_reward': 0, 'sharpe_ratio': 0,
            'max_drawdown': 0, 'avg_hold_time_overall': "0h", 'avg_hold_time_winners': "0h",
            'avg_hold_time_losers': "0h", 'avg_hold_time_scratches': "0h", 'avg_mfe': 0,
            'avg_mae': 0, 'total_commissions': 0, 'total_fees': 0, 'sqn': 0, 'k_ratio': 0,
            'kelly_percent': 0, 'p_value': 1.0, 'balances': []
        }
    
    def getComplete(self):
        """Calcular todas las estadísticas de performance"""
        if self.trades is None or len(self.trades) == 0:
            return self.getEmpty()

        total_trades = len(self.trades)
        
        # Extraer datos básicos
        volumes = [getattr(trade, 'exit_quantity', 0) for trade in self.trades if hasattr(trade, 'exit_quantity')]
        commissions = [getattr(trade, 'commission', 0) for trade in self.trades if hasattr(trade, 'commission')]
        fees = [getattr(trade, 'fees', 0) for trade in self.trades if hasattr(trade, 'fees')]
        total_commissions = sum(commissions)
        total_fees = sum(fees)
        
        # ===== ESTADÍSTICAS BÁSICAS =====
        stats = self.getStats(mode='net')
        stats_gross = self.getStats( mode='gross')
        
        # ===== TIEMPO DE MANTENIMIENTO =====
        hold_times = self.calculateHoldTimes()
        
        # MFE/MAE (Maximum Favorable/Adverse Excursion)
        mfe_mae_stats = self.calculateMaximumExecutions()
        
        # ===== COMPILAR RESULTADO =====
        return {
            'net': stats,
            'gross': stats_gross,
            'total_trades': total_trades,
            'total_commissions': round(total_commissions, 2),
            'total_fees': round(total_fees, 2),
            
            # Tiempo de mantenimiento
            'avg_hold_time_overall': hold_times['overall'],
            'avg_hold_time_winners': hold_times['winners'],
            'avg_hold_time_losers': hold_times['losers'],
            'avg_hold_time_scratches': hold_times['scratches'],
            
            # MFE/MAE
            'avg_mfe': round(mfe_mae_stats['avg_mfe'], 2),
            'avg_mae': round(mfe_mae_stats['avg_mae'], 2),
        }
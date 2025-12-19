"""
Servicios para cálculo de performance y estadísticas de trading
Migración de journal/src/performance.py
"""
from typing import List, Dict, Optional
from collections import defaultdict
import numpy as np
from datetime import datetime

from app.schemas import PerformanceStats, SymbolPerformance, BestWorstSymbols


class PerformanceCalculator:
    """Calcula estadísticas de performance de trades"""
    
    def __init__(self, trades_data: List[Dict], gross: bool = False):
        """
        Args:
            trades_data: Lista de diccionarios con datos de trades
            gross: Si incluir comisiones en el cálculo
        """
        self.trades_data = trades_data
        self.gross = gross
        self.pnl_values = self._extract_pnl_values()
    
    def _extract_pnl_values(self) -> List[float]:
        """Extrae valores de P&L de los trades"""
        pnl = []
        for trade in self.trades_data:
            if self.gross:
                pnl.append(trade.get('profit_loss', 0) + trade.get('commission', 0))
            else:
                pnl.append(trade.get('profit_loss', 0))
        return pnl
    
    def _mean(self, numbers: List[float]) -> Optional[float]:
        """Calcula promedio"""
        if not numbers:
            return None
        return float(np.mean([n for n in numbers if n is not None]))
    
    def _median(self, numbers: List[float]) -> Optional[float]:
        """Calcula mediana"""
        if not numbers:
            return None
        return float(np.median([n for n in numbers if n is not None]))
    
    def _std(self, numbers: List[float]) -> Optional[float]:
        """Calcula desviación estándar"""
        if not numbers or len(numbers) < 2:
            return 0
        return float(np.std([n for n in numbers if n is not None]))
    
    def calculate_max_drawdown(self) -> float:
        """Calcula máximo drawdown"""
        if not self.pnl_values:
            return 0
        
        cumulative_pnl = 0
        peak = 0
        max_dd = 0
        
        for pnl in self.pnl_values:
            cumulative_pnl += pnl
            if cumulative_pnl > peak:
                peak = cumulative_pnl
            drawdown = peak - cumulative_pnl
            if drawdown > max_dd:
                max_dd = drawdown
        
        return max_dd if peak != 0 else 0
    
    def calculate_streaks(self) -> Dict[str, int]:
        """Calcula rachas consecutivas máximas"""
        if not self.pnl_values:
            return {'max_wins': 0, 'max_losses': 0}
        
        max_wins = 0
        max_losses = 0
        current_wins = 0
        current_losses = 0
        
        for pnl in self.pnl_values:
            if pnl > 0:
                current_wins += 1
                current_losses = 0
                max_wins = max(max_wins, current_wins)
            elif pnl < 0:
                current_losses += 1
                current_wins = 0
                max_losses = max(max_losses, current_losses)
            else:
                current_wins = 0
                current_losses = 0
        
        return {'max_wins': max_wins, 'max_losses': max_losses}
    
    def calculate_daily_stats(self) -> Dict:
        """Calcula estadísticas diarias"""
        if not self.trades_data:
            return {}
        
        days = list(set([datetime.fromisoformat(d['exit_date']).date() if isinstance(d['exit_date'], str) else d['exit_date'].date() 
                         for d in self.trades_data if d.get('exit_date')]))
        
        profits = {}
        for day in days:
            day_trades = [d for d in self.trades_data 
                         if (datetime.fromisoformat(d['exit_date']).date() if isinstance(d['exit_date'], str) else d['exit_date'].date()) == day]
            day_pnl = sum([(d['profit_loss'] + (d['commission'] if self.gross else 0)) for d in day_trades])
            profits[day] = day_pnl
        
        wins = [v for v in profits.values() if v > 0]
        losses = [v for v in profits.values() if v < 0]
        total_pnl = sum(self.pnl_values)
        total_volume = sum(d.get('exit_quantity', 0) for d in self.trades_data)
        
        return {
            'avg_daily_pnl': total_pnl / len(days) if len(days) > 0 else 0,
            'avg_daily_volume': total_volume / len(days) if len(days) > 0 else 0,
            'avg_win_per_day': self._mean(wins) if len(wins) else 0,
            'avg_loss_per_day': self._mean(losses) if len(losses) else 0,
            'daily_winrate': (len(wins) / len(days)) if len(days) > 0 else 0,
            'avg_trades_per_day': len(self.trades_data) / len(days) if len(days) > 0 else 0,
        }
    
    def get_stats(self, scratch_percentage: float = 0.01) -> PerformanceStats:
        """Calcula todas las estadísticas de performance"""
        
        total_pnl = sum(self.pnl_values)
        total_quantity = sum([d.get('exit_quantity', 0) for d in self.trades_data])
        total_trades = len(self.pnl_values)
        
        winning_pnl = [p for p in self.pnl_values if p > 0]
        losing_pnl = [p for p in self.pnl_values if p < 0]
        
        avg_trade_pnl = self._mean(self.pnl_values) if self.pnl_values else 0
        avg_pnl_per_share = total_pnl / total_quantity if total_quantity != 0 else 0
        median_trade_pnl = self._median(self.pnl_values) if self.pnl_values else 0
        avg_win = self._mean(winning_pnl) if winning_pnl else 0
        avg_loss = self._mean(losing_pnl) if losing_pnl else 0
        
        scratch_threshold = abs(avg_trade_pnl) * scratch_percentage
        winning_trades = len([p for p in self.pnl_values if p > scratch_threshold])
        losing_trades = len([p for p in self.pnl_values if p < -scratch_threshold])
        scratch_trades = len([p for p in self.pnl_values if -scratch_threshold <= p <= scratch_threshold])
        
        largest_gain = max(self.pnl_values) if self.pnl_values else 0
        largest_loss = min(self.pnl_values) if self.pnl_values else 0
        
        risk_reward = avg_win / abs(avg_loss) if avg_loss != 0 else 0
        
        total_wins = sum(winning_pnl) if winning_pnl else 0
        total_losses = abs(sum(losing_pnl)) if losing_pnl else 0
        profit_factor = total_wins / total_losses if total_losses > 0 else (1e99 if total_wins > 0 else 0)
        
        trade_pnl_std = self._std(self.pnl_values) if len(self.pnl_values) > 1 else 0
        sharpe_ratio = (avg_trade_pnl / trade_pnl_std) if trade_pnl_std != 0 else 0
        
        max_drawdown = self.calculate_max_drawdown()
        streaks = self.calculate_streaks()
        daily_stats = self.calculate_daily_stats()
        
        return PerformanceStats(
            total_pnl=round(total_pnl, 2),
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            scratch_trades=scratch_trades,
            win_rate=round((winning_trades / total_trades * 100) if total_trades > 0 else 0, 2),
            loss_rate=round((losing_trades / total_trades * 100) if total_trades > 0 else 0, 2),
            winning_pnl=round(sum(winning_pnl), 2),
            losing_pnl=round(sum(losing_pnl), 2),
            avg_trade_pnl=round(avg_trade_pnl, 2),
            avg_pnl_per_share=round(avg_pnl_per_share, 4),
            median_trade_pnl=round(median_trade_pnl, 2),
            avg_win=round(avg_win, 2),
            avg_loss=round(avg_loss, 2),
            largest_gain=round(largest_gain, 2),
            largest_loss=round(largest_loss, 2),
            risk_reward=round(risk_reward, 2),
            total_wins=round(total_wins, 2),
            total_losses=round(total_losses, 2),
            profit_factor=round(profit_factor, 2),
            trade_pnl_std=round(trade_pnl_std, 2),
            sharpe_ratio=round(sharpe_ratio, 2),
            max_drawdown=round(max_drawdown, 2),
            sqn=0,
            k_ratio=0,
            kelly_percent=0,
            p_value=1.0,
            max_consecutive_wins=streaks['max_wins'],
            max_consecutive_losses=streaks['max_losses'],
            avg_daily_pnl=round(daily_stats.get('avg_daily_pnl', 0), 2),
            avg_daily_volume=round(daily_stats.get('avg_daily_volume', 0), 2),
            avg_win_per_day=round(daily_stats.get('avg_win_per_day', 0), 2),
            avg_loss_per_day=round(daily_stats.get('avg_loss_per_day', 0), 2),
            daily_winrate=round(daily_stats.get('daily_winrate', 0) * 100, 2),
            avg_trades_per_day=round(daily_stats.get('avg_trades_per_day', 0), 2),
        )


class SymbolPerformanceCalculator:
    """Calcula performance por símbolo"""
    
    def __init__(self, trades_data: List[Dict], gross: bool = False):
        self.trades_data = trades_data
        self.gross = gross
        self.pnl_values = self._extract_pnl_values()
    
    def _extract_pnl_values(self) -> List[float]:
        """Extrae valores de P&L de los trades"""
        pnl = []
        for trade in self.trades_data:
            if self.gross:
                pnl.append(trade.get('profit_loss', 0) + trade.get('commission', 0))
            else:
                pnl.append(trade.get('profit_loss', 0))
        return pnl
    
    def _mean(self, numbers: List[float]) -> Optional[float]:
        if not numbers:
            return None
        return float(np.mean([n for n in numbers if n is not None]))
    
    def get_best_and_worst_symbols(self, top_n: int = 5) -> BestWorstSymbols:
        """Obtiene los mejores y peores símbolos"""
        
        symbol_stats = defaultdict(lambda: {'pnl': [], 'wins': 0, 'total': 0})
        
        for i, trade in enumerate(self.trades_data):
            symbol = trade.get('symbol', '')
            pnl = self.pnl_values[i] if i < len(self.pnl_values) else 0
            
            symbol_stats[symbol]['pnl'].append(pnl)
            symbol_stats[symbol]['total'] += 1
            if pnl > 0:
                symbol_stats[symbol]['wins'] += 1
        
        # Construir lista de símbolos con estadísticas
        symbol_list = []
        for symbol, stat in symbol_stats.items():
            total_pnl = sum(stat['pnl'])
            avg_pnl = self._mean(stat['pnl']) or 0
            win_rate = (stat['wins'] / stat['total'] * 100) if stat['total'] > 0 else 0
            winning_pnl = [p for p in stat['pnl'] if p > 0]
            losing_pnl = [p for p in stat['pnl'] if p < 0]
            avg_win = self._mean(winning_pnl) or 0
            avg_loss = self._mean(losing_pnl) or 0
            
            symbol_list.append(SymbolPerformance(
                symbol=symbol,
                total_pnl=round(total_pnl, 2),
                avg_pnl=round(avg_pnl, 2),
                win_rate=round(win_rate, 1),
                trade_count=stat['total'],
                avg_win=round(avg_win, 2),
                avg_loss=round(avg_loss, 2),
            ))
        
        # Ordenar por total P&L
        symbol_list_sorted = sorted(symbol_list, key=lambda x: x.total_pnl, reverse=True)
        
        # Top N mejores y peores
        best = symbol_list_sorted[:top_n]
        worst = symbol_list_sorted[-top_n:][::-1]
        
        return BestWorstSymbols(best=best, worst=worst)

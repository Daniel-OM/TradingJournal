
import json
from datetime import datetime, date
from collections import defaultdict
import asyncio
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
from sqlalchemy import and_

from ..models.trade import Trade
from ..models.watchlist import Watchlist
from ..models.watchlist_entry import WatchlistEntry
from ..models.candle import Candle

class BinInterval:

    def __init__(self, left, right, closed='left'):
        self.pd_interval = pd.Interval(left, right, closed)
        self.left = left
        self.right = right
        self.closed = closed
    
    @property
    def middle(self):
        return (self.left + self.right) / 2
    
    @property
    def interval(self):
        return [self.left, self.right]
    
    def isInside(self, value):
        if self.closed == 'left':
            return self.left <= value < self.right
        elif self.closed == 'right':
            return self.left < value <= self.right
        elif self.closed == 'both':
            return self.left <= value <= self.right
        elif self.closed == 'neither':
            return self.left < value < self.right
        else:
            return self.left <= value < self.right
    
    def __repr__(self): # How to print an individual object
        return f'[{self.left}, {self.right}]'
    
    def __str__(self): # How to print an object in a list
        return f'[{self.left}, {self.right}]'

class ChartBins:

    def __init__(self, values, max_bins:int=50, min_bins:int=10) -> None:
        self.values = np.array(values)
        self.max_bins: int = max_bins
        self.min_bins: int = min_bins
        self.bins: int = 0
        self.periods: list = []
        self.categories: list = []

    def calculateBins(self, values=None, max_bins:int=None, min_bins:int=None) -> int:
        """Calcula número de bins automáticamente usando Freedman-Diaconis."""

        if values is None: 
            values = self.values
        else: 
            values = np.array(values)
        if max_bins is None: max_bins = self.max_bins
        if min_bins is None: min_bins = self.min_bins

        if len(values) < 2:
            return 1  # mínimo 1 bin
        q75, q25 = np.percentile(values, [75, 25])
        iqr = q75 - q25
        bin_width = 2 * iqr / (len(values) ** (1/3)) if iqr > 0 else 1
        bins = int(np.ceil((max(values) - min(values)) / bin_width))
        self.bins: int = min(max(bins, min_bins), max_bins)

        return self.bins
    
    def getIntervals(self, values=None) -> tuple[list[BinInterval], list]:
        
        if values is None: 
            values = self.values
        else: 
            values = np.array(values)

        if self.bins == 0:
            self.calculateBins(values=values)
        
        arr = np.linspace(min(values), max(values), num=self.bins)
        self.periods: list[BinInterval] = [BinInterval(left=v, right=arr[i+1], closed='left') for i, v in enumerate(arr[:-1])]
        self.categories = [p.middle for p in self.periods]

        return self.periods, self.categories
    
    def getRowsBin(self, values=None):
        
        if values is None: 
            values = self.values
        else: 
            values = np.array(values)

        if len(self.periods) <= 0:
            self.getIntervals(values=values)

        return [p.pd_interval for v in values for p in self.periods if p.isInside(v)]
    
    def getBinData(self, values=None):
        
        if values is None: 
            values = self.values
        else: 
            values = np.array(values)

        if len(self.periods) <= 0:
            self.getIntervals(values=values)

        return {p: [v for v in values if p.isInside(v)] for p in self.periods}

class Agrupations:

    def __init__(self, data) -> None:
        self.data = data

    def bins(self, max_bins:int=50, min_bins:int=50):

        data = self.data.copy()
        price_bins = ChartBins(values=data["price"], max_bins=max_bins, min_bins=min_bins)
        price_intervals = price_bins.getIntervals()[0] # pd.cut(df["price"], bins=price_bins_count).cat.categories
        time_bins = ChartBins(values=data['index'], max_bins=max_bins, min_bins=min_bins)
        time_intervals = time_bins.getIntervals()[0]

        max_df = pd.DataFrame(data=[[data[(data['is_max'] == True) & (price_interval.left <= data['price']) & (data['price'] < price_interval.right) & 
                                            (time_interval.left <= data['index']) & (data['index'] < time_interval.right)].shape[0] \
                                         for price_interval in price_intervals] for time_interval in time_intervals], 
                                  columns=[interval.middle for interval in price_intervals], 
                                  index=[interval.middle for interval in time_intervals])
        min_df = pd.DataFrame(data=[[data[(data['is_min'] == True) & (price_interval.left <= data['price']) & (data['price'] < price_interval.right) & 
                                            (time_interval.left <= data['index']) & (data['index'] < time_interval.right)].shape[0] \
                                         for price_interval in price_intervals] for time_interval in time_intervals], 
                                  columns=[interval.middle for interval in price_intervals], 
                                  index=[interval.middle for interval in time_intervals])
        return max_df, min_df

    def dbscan(self, max_distance:float=0.2, min_samples:int=2, libraries:bool=False):
        
        data = self.data.copy()
        data['index'] = (data['index']/60).astype(int)
        X = data[['index', 'price']].values
    
        if libraries:
            from sklearn.cluster import DBSCAN
            from sklearn.preprocessing import StandardScaler
            
            X_scaled = StandardScaler().fit_transform(X)
            clustering = DBSCAN(eps=max_distance, min_samples=min_samples).fit(X_scaled)
            data['cluster'] = clustering.labels_

        else:
            
            # Normalización manual (StandardScaler equivalente)
            mean = X.mean(axis=0)
            std = X.std(axis=0)
            X_scaled = (X - mean) / std
            
            # DBSCAN implementación manual
            n_points = len(X_scaled)
            labels = np.full(n_points, -1)  # -1 = ruido
            cluster_id = 0
            
            def get_neighbors(point_idx):
                distances = np.sqrt(np.sum((X_scaled - X_scaled[point_idx])**2, axis=1))
                return np.where(distances <= max_distance)[0]
            
            def expand_cluster(point_idx, neighbors, cluster_id):
                labels[point_idx] = cluster_id
                i = 0
                while i < len(neighbors):
                    neighbor_idx = neighbors[i]
                    
                    if labels[neighbor_idx] == -1:  # Era ruido
                        labels[neighbor_idx] = cluster_id
                    
                    if labels[neighbor_idx] == -1 or labels[neighbor_idx] == -2:  # No visitado
                        labels[neighbor_idx] = cluster_id
                        new_neighbors = get_neighbors(neighbor_idx)
                        
                        if len(new_neighbors) >= min_samples:
                            neighbors = np.concatenate([neighbors, new_neighbors])
                    
                    i += 1
            
            # Marcar todos como no visitados
            visited = np.zeros(n_points, dtype=bool)
            
            for point_idx in range(n_points):
                if visited[point_idx]:
                    continue
                
                visited[point_idx] = True
                neighbors = get_neighbors(point_idx)
                
                if len(neighbors) < min_samples:
                    labels[point_idx] = -1  # Ruido
                else:
                    expand_cluster(point_idx, neighbors, cluster_id)
                    cluster_id += 1
            
            data['cluster'] = labels
            
        cluster_counts = data.groupby('cluster').size()
        centroids = data.groupby('cluster')[['index', 'price']].mean()
        print(cluster_counts)
        print(centroids)

        return data.copy()

    def kde(self, x_points:int=100, y_points:int=100, libraries:bool=False):
        
        data = self.data
        points = np.vstack([data['index'], data['price']])
            
        if libraries:
            from scipy.stats import gaussian_kde

            kde = gaussian_kde(points)

            # generar grilla suave
            xi, yi = np.meshgrid(
                np.linspace(data['index'].min(), data['index'].max(), x_points),
                np.linspace(data['price'].min(), data['price'].max(), y_points)
            )
            zi = kde(np.vstack([xi.flatten(), yi.flatten()]))

        else:
            # KDE manual con kernel gaussiano
            def gaussian_kernel(distances, bandwidth):
                return (1 / np.sqrt(2 * np.pi)) * np.exp(-0.5 * (distances / bandwidth)**2)
            
            # Calcular bandwidth usando regla de Scott
            n = points.shape[1]
            d = points.shape[0]
            bandwidth = n**(-1./(d+4))
            
            # Ajustar bandwidth por la escala de los datos
            std_devs = np.std(points, axis=1)
            bandwidth = bandwidth * std_devs[:, np.newaxis]
            
            # Generar grilla
            xi, yi = np.meshgrid(
                np.linspace(data['index'].min(), data['index'].max(), x_points),
                np.linspace(data['price'].min(), data['price'].max(), y_points)
            )
            
            grid_points = np.vstack([xi.flatten(), yi.flatten()])
            
            # Calcular densidad en cada punto de la grilla
            zi = np.array(np.mean(gaussian_kernel(np.sqrt(np.sum(((points - grid_points[:, i:i+1]) / bandwidth)**2, axis=0)), 1.0)) 
                          for i in range(grid_points.shape[1]))
            
        heatmap = zi.reshape(xi.shape)

        return heatmap

    def gmm(self, n_components:int=5, covariance_type:str='full', libraries:bool=False):

        data = self.data
        X = data[['index','price']].values
        
        if libraries:
            from sklearn.mixture import GaussianMixture

            gmm = GaussianMixture(n_components=n_components, covariance_type=covariance_type).fit(X)
            probs = np.exp(gmm.score_samples(X))
            data['prob'] = probs

        else:
            n_samples, n_features = X.shape
            
            # Inicialización con K-means simple
            np.random.seed(42)
            indices = np.random.choice(n_samples, n_components, replace=False)
            means = X[indices].copy()
            
            # Covarianzas iniciales
            if covariance_type == 'full':
                covariances = np.array([np.eye(n_features) for _ in range(n_components)])
            else:  # 'diag' o 'spherical'
                covariances = np.ones((n_components, n_features))
            
            weights = np.ones(n_components) / n_components
            
            # EM algorithm
            max_iter = 100
            tol = 1e-4
            
            def multivariate_gaussian(X, mean, cov):
                n = X.shape[0]
                diff = X - mean
                if covariance_type == 'full':
                    inv_cov = np.linalg.inv(cov)
                    det_cov = np.linalg.det(cov)
                    exp_term = -0.5 * np.sum(diff @ inv_cov * diff, axis=1)
                else:
                    inv_cov = 1.0 / cov
                    det_cov = np.prod(cov)
                    exp_term = -0.5 * np.sum((diff**2) * inv_cov, axis=1)
                
                norm_const = 1.0 / np.sqrt((2 * np.pi)**n_features * det_cov)
                return norm_const * np.exp(exp_term)
            
            for iteration in range(max_iter):
                # E-step: calcular responsabilidades
                responsibilities = np.zeros((n_samples, n_components))
                
                for k in range(n_components):
                    responsibilities[:, k] = weights[k] * multivariate_gaussian(
                        X, means[k], covariances[k]
                    )
                
                # Normalizar responsabilidades
                resp_sum = responsibilities.sum(axis=1, keepdims=True)
                resp_sum[resp_sum == 0] = 1e-10
                responsibilities /= resp_sum
                
                # M-step: actualizar parámetros
                Nk = responsibilities.sum(axis=0)
                
                means_old = means.copy()
                
                for k in range(n_components):
                    # Actualizar pesos
                    weights[k] = Nk[k] / n_samples
                    
                    # Actualizar medias
                    means[k] = (responsibilities[:, k:k+1] * X).sum(axis=0) / Nk[k]
                    
                    # Actualizar covarianzas
                    diff = X - means[k]
                    if covariance_type == 'full':
                        covariances[k] = (responsibilities[:, k:k+1] * diff).T @ diff / Nk[k]
                        covariances[k] += 1e-6 * np.eye(n_features)  # regularización
                    else:
                        covariances[k] = np.sum(responsibilities[:, k:k+1] * diff**2, axis=0) / Nk[k]
                        covariances[k] += 1e-6  # regularización
                
                # Verificar convergencia
                if np.linalg.norm(means - means_old) < tol:
                    break
            
            # Calcular probabilidades finales
            probs = np.zeros(n_samples)
            for k in range(n_components):
                probs += weights[k] * multivariate_gaussian(X, means[k], covariances[k])

        return data.copy()



class Stats:

    def __init__(self, data:list[dict], gross:bool=False) -> None:
        '''
        data: list[dict]
            Should be a list with dictionaries with at least the following attributes:
            {
                'entry_date': 2025-09-10,
                'exit_date': 2025-09-15,
                'symbol': 'XXX',
                'entry_price': 1.0,
                'exit_price': 2.0,
                'side': True, # True is for LONG and False for SHORT
                'profit_loss': 15.63,
                'exit_quantity': 1, # This should be 1 for watchlist entries and the quantity for trades
                'commission': 0,
                'candles': list[Candle] --- Optional, only if calculating MFE/MAE
            }
        '''
        self.data: list[dict] = data
        self.gross: bool = gross
        self.date_format = '%Y-%m-%d'
        self.time_format = '%H:%M:%S'

    def mean(self, numbers):
        return float(np.mean([n for n in numbers if n is not None])) if (isinstance(numbers, pd.Series) and not numbers.empty) or (isinstance(numbers, np.ndarray) and numbers.size > 0) or numbers else None

    def median(self, numbers):
        return float(np.median([n for n in numbers if n is not None])) if (isinstance(numbers, pd.Series) and not numbers.empty) or (isinstance(numbers, np.ndarray) and numbers.size > 0) or numbers else None

    def std(self, numbers):
        return float(np.std([n for n in numbers if n is not None])) if (isinstance(numbers, pd.Series) and not numbers.empty) or (isinstance(numbers, np.ndarray) and numbers.size > 0) or numbers else None

    def max(self, numbers):
        return float(np.max([n for n in numbers if n is not None])) if (isinstance(numbers, pd.Series) and not numbers.empty) or (isinstance(numbers, np.ndarray) and numbers.size > 0) or numbers else None

    def min(self, numbers):
        return float(np.min([n for n in numbers if n is not None])) if (isinstance(numbers, pd.Series) and not numbers.empty) or (isinstance(numbers, np.ndarray) and numbers.size > 0) or numbers else None

    def _normal_cdf(self, x) -> float:
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

    def _t_test_p_value_approx(self, t_stat, df:int) -> float:
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

    async def calculateMaxDrawDown(self, pnl_values:list[float]):
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

    async def calculateAdvancedStats(self, pnl_values:list[float]) -> dict:
        """Calcular estadísticas avanzadas (Gold)"""
        if not pnl_values or len(pnl_values) < 2:
            return {'sqn': 0, 'k_ratio': 0, 'kelly_percent': 0, 'p_value': 1.0}
        
        # SQN (System Quality Number)
        avg_pnl = self.mean(pnl_values)
        std_pnl = self.std(pnl_values)
        sqn = (avg_pnl / std_pnl) * (len(pnl_values)**1/2) if std_pnl != 0 else 0
        
        # K-Ratio (simplificado)
        cumulative_pnl = np.cumsum(pnl_values)
        if len(cumulative_pnl) > 1:
            slope = np.polyfit(range(len(cumulative_pnl)), cumulative_pnl, 1)[0]
            residuals = cumulative_pnl - np.polyval([slope, 0], range(len(cumulative_pnl)))
            std_residuals = self.std(residuals)
            k_ratio = float(slope / std_residuals) if std_residuals != 0 else 0
        else:
            k_ratio = 0
        
        # Kelly % (simplificado)
        win_rate = len([p for p in pnl_values if p > 0]) / len(pnl_values)
        if win_rate > 0 and win_rate < 1:
            avg_win = self.mean([p for p in pnl_values if p > 0])
            avg_loss = abs(self.mean([p for p in pnl_values if p < 0])) if any(p < 0 for p in pnl_values) else 1
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

    async def calculateStreaks(self, pnl_values:list[float]) -> dict[str, int]:
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

    async def calculateDailyStats(self) -> dict[str, float]:
        """Calcular estadísticas diarias"""
        
        # Determinar rango de fechas
        start_date = min((d['entry_date'] for d in self.data if d['entry_date']), default=None)
        end_date = max((d['entry_date'] for d in self.data if d['entry_date']), default=None)

        if start_date and end_date:
            trading_days = (end_date - start_date).days + 1
        else:
            first_trade = min(self.data, key=lambda t: t['entry_date'])
            last_trade = max(self.data, key=lambda t: t['entry_date'])
            trading_days = (last_trade['entry_date'] - first_trade['entry_date']).days + 1
        
        if trading_days == 0:
            trading_days = 1
        
        total_pnl = sum((d['profit_loss'] + d['commission'] if self.gross else d['profit_loss']) for d in self.data)
        total_volume = sum(d.get('exit_quantity', 0) for d in self.data)
        
        return {
            'avg_daily_pnl': total_pnl / trading_days,
            'avg_daily_volume': total_volume / trading_days
        }

    async def getStats(self, values:list=None, scratch_percentage:float=0.01):

        if values is None:
            pnl_values = [(d['profit_loss'] + d['commission'] if self.gross else d['profit_loss']) for d in self.data]
        else:
            pnl_values = values

        total_pnl = sum(pnl_values)
        total_quantity = sum([d['exit_quantity'] for d in self.data if hasattr(d, 'exit_quantity')]) if self.data else 0
        total_trades = len(pnl_values)
        
        winning_pnl = [p for p in pnl_values if p > 0]
        losing_pnl = [p for p in pnl_values if p < 0]
        
        avg_trade_pnl = self.mean(pnl_values) if pnl_values else 0
        avg_pnl_per_share = total_pnl / total_quantity if total_quantity != 0 else 0
        median_trade_pnl = self.median(pnl_values) if pnl_values else 0
        avg_win = self.mean(winning_pnl) if winning_pnl else 0
        avg_loss = self.mean(losing_pnl) if losing_pnl else 0

        scratch_threshold = abs(avg_trade_pnl) * scratch_percentage
        winning_trades = len([p for p in pnl_values if p > scratch_threshold])
        losing_trades = len([p for p in pnl_values if p < -scratch_threshold])
        scratch_trades = len([p for p in pnl_values if -scratch_threshold < p and p < scratch_threshold])
        
        largest_gain = max(pnl_values) if pnl_values else 0
        largest_loss = min(pnl_values) if pnl_values else 0
        
        # Risk/Reward y Profit Factor
        risk_reward = avg_win / abs(avg_loss) if avg_loss != 0 else 0
        
        total_wins = sum(winning_pnl) if winning_pnl else 0
        total_losses = abs(sum(losing_pnl)) if losing_pnl else 0
        profit_factor = total_wins / total_losses if total_losses > 0 else 1e99 if total_wins > 0 else 0
        
        # Desviación estándar
        trade_pnl_std = self.std(pnl_values) if len(pnl_values) > 1 else 0
        
        # Sharpe Ratio
        sharpe_ratio = (avg_trade_pnl / trade_pnl_std) if trade_pnl_std != 0 else 0
        

        max_drawdown, advanced_stats, consecutive_stats, daily_stats = await asyncio.gather(
            self.calculateMaxDrawDown(pnl_values=pnl_values),
            self.calculateAdvancedStats(pnl_values=pnl_values),
            self.calculateStreaks(pnl_values=pnl_values),
            self.calculateDailyStats()
        )
        
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

            'sqn': round(advanced_stats.get('sqn', 0), 2),
            'k_ratio': round(advanced_stats.get('k_ratio', 0), 2),
            'kelly_percent': round(advanced_stats.get('kelly_percent', 0), 2),
            'p_value': round(advanced_stats.get('p_value', 0), 4),
            
            # Rachas
            'max_consecutive_wins': consecutive_stats['max_wins'],
            'max_consecutive_losses': consecutive_stats['max_losses'],

            'avg_daily_pnl': round(daily_stats['avg_daily_pnl'], 2),
            'avg_daily_volume': round(daily_stats['avg_daily_volume'], 2),
        }

    async def calculateMaximumExecutions(self):
        """Calcular Maximum Favorable/Adverse Excursion"""
        mfe_values = []
        mae_values = []
        
        for d in self.data:
            mae = max((d['entry_price'] - candle['low'] if d['side'] else candle['high'] - d['entry_price']) / d['entry_price'] 
                            for candle in d['candles'])
            mfe = max((candle['high'] - d['entry_price'] if d['side'] else d['entry_price'] - candle['low']) / d['entry_price'] 
                            for candle in d['candles'])
            
            if (d['side'] and (d['entry_price'] - d['exit_price']) / d['entry_price'] != mae) or \
                (not d['side'] and (d['exit_price'] - d['entry_price']) / d['entry_price'] != mae): 
                mae_values.append(mae)
            if (d['side'] and (d['exit_price'] - d['entry_price']) / d['entry_price'] != mfe) or \
                (not d['side'] and (d['entry_price'] - d['exit_price']) / d['entry_price'] != mfe): 
                mfe_values.append(mfe)
        
        return {
            'avg_mfe': self.mean(mfe_values) if mfe_values else 0,
            'avg_mae': self.mean(mae_values) if mae_values else 0
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

    async def calculateHoldTimes(self):
        """Calcular tiempos de mantenimiento promedio"""
        def get_hold_time(d:dict):
            if 'exit_date' in d and 'entry_date' in d and d['entry_date']:
                exit_date = d['exit_date'] or (datetime.now() if isinstance(d['entry_date'], datetime) else date.today())
                return (exit_date - d['entry_date']).total_seconds() / 60
            
            return 0
        
        hold_times_all = []
        hold_times_winners = []
        hold_times_losers = []
        hold_times_scratches = []
        
        for d in self.data:
            hold_time = get_hold_time(d)
            hold_times_all.append(hold_time)
            
            if d['profit_loss'] > 0:
                hold_times_winners.append(hold_time)
            elif d['profit_loss'] < 0:
                hold_times_losers.append(hold_time)
            else:
                hold_times_scratches.append(hold_time)

        return {
            'overall': self._formatHoldTime(self.mean(hold_times_all)) if hold_times_all else "0h",
            'winners': self._formatHoldTime(self.mean(hold_times_winners)) if hold_times_winners else "0h",
            'losers': self._formatHoldTime(self.mean(hold_times_losers)) if hold_times_losers else "0h",
            'scratches': self._formatHoldTime(self.mean(hold_times_scratches)) if hold_times_scratches else "0h",
        }

    async def getEmpty(self):

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

class Charts:

    def __init__(self, data:list[dict], gross:bool=False) -> None:
        '''
        data: list[dict]
            Should be a list with dictionaries with at least the following attributes:
            {
                'entry_date': 2025-09-10,
                'exit_date': 2025-09-15,
                'symbol': 'XXX',
                'entry_price': 1.0,
                'exit_price': 2.0,
                'side': True, # True is for LONG and False for SHORT
                'profit_loss': 15.63,
                'exit_quantity': 1, # This should be 1 for watchlist entries and the quantity for trades
                'commission': 0,
                'candles': list[Candle] --- Optional, only if calculating MFE/MAE
            }
        '''
        self.date_format: str = '%Y-%m-%d'
        self.time_format: str = '%H:%M:%S'
        self.data: list[dict] = data
        self.gross: bool = gross
        self.getPnl()

    def getPnl(self) -> None:
        if not self.data:
            self.pnl_values: list = []
        else:
            self.pnl_values: list = [(d['profit_loss'] + d['commission'] if self.gross else d['profit_loss']) for d in self.data]

    async def getEquityCurve(self) -> dict:
        """Gráfico de curva de equity (P&L acumulativo)"""
        
        if not self.data or not self.pnl_values or len(self.pnl_values) <= 0:
            return {'dates': [], 'equity': [], 'drawdown': []}
        
        dates = []
        equity = [0]
        peak = 0
        drawdowns = [0]
        for i, value in enumerate(self.pnl_values):
            dates.append(self.data[i]['entry_date'].strftime('%Y-%m-%d')) # TODO: Should take into account multiple days positions for swing trading 
            current_equity = equity[-1] + value
            equity.append(current_equity)
            
            # Calcular drawdown
            if current_equity > peak:
                peak = current_equity
            drawdowns.append(-(peak - current_equity))
        
        return {
            'dates': dates,
            'equity': equity[1:],
            'drawdown': drawdowns[1:],
            'chart_type': 'line'
        }
        
    async def getPnlTimeHistogram(self, mode:str='daily') -> dict:
        """
        P&L histogram with time aggregation
        
        mode: str
            Can be 'daily' or 'monthly'
        """
        if mode == 'monthly':
            x_axis = 'months'
            time_format = '%Y-%m'
        else:
            x_axis = 'dates'
            time_format = '%Y-%m-%d'
            
        if not self.data or not self.pnl_values or len(self.pnl_values) <= 0:
            return {x_axis: [], 'pnl': []}
        
        time_pnl = defaultdict(float)
        
        for i, d in enumerate(self.data):
            time_key: str = d['entry_date'].strftime(time_format)
            time_pnl[time_key] += (d['profit_loss'] + d['commission'] if self.gross else d['profit_loss']) \
                                if len(self.pnl_values) <= 0 else self.pnl_values[i]
        
        sorted_dates: list = sorted(time_pnl.keys())
        
        return {
            x_axis: sorted_dates,
            'pnl': [time_pnl[date] for date in sorted_dates],
            'chart_type': 'bar'
        }
    
    async def getPnlDistribution(self) -> dict:
        """Histograma de distribución de P&L por trade"""
        if not self.pnl_values or len(self.pnl_values) <= 0:
            return {'bins': [], 'counts': []}
        
        # Crear bins automáticamente
        min_pnl: float = min(self.pnl_values)
        max_pnl: float = max(self.pnl_values)
        
        if min_pnl == max_pnl:
            return {'bins': [min_pnl], 'counts': [len(self.pnl_values)]}
        
        # Crear 20 bins
        n_bins: int = min(20, len(self.pnl_values))
        bin_edges: np.ndarray = np.linspace(min_pnl, max_pnl, n_bins + 1)
        bin_centers: list = [(bin_edges[i] + bin_edges[i+1]) / 2 for i in range(len(bin_edges)-1)]
        
        counts, _ = np.histogram(self.pnl_values, bins=bin_edges)
        
        return {
            'bins': [round(center, 2) for center in bin_centers],
            'counts': counts.tolist(),
            'chart_type': 'histogram'
        }
    
    def _getStatRequirements(self, prev:dict, pnl:float) -> dict:

        prev['pnl'].append(pnl)
        prev['total'] += 1
        if prev['pnl'][-1] > 0:
            prev['win'] += prev['pnl'][-1]
            prev['wins'] += 1
        elif prev['pnl'][-1] < 0:
            prev['loss'] += prev['pnl'][-1]

        return prev

    def _calculateStats(self, data:dict) -> tuple[float, float, float, float, float, float, float]:

        total_pnl = np.sum(data['pnl'])
        avg_pnl = np.mean(data['pnl'])
        avg_win = data['win'] / data['wins'] if data['wins'] > 0 else 0
        avg_loss = data['loss'] / (data['total']-data['wins']) if (data['total']-data['wins']) > 0 else 0
        win_rates = data['wins'] / data['total'] * 100 if data['total'] > 0 else 0
        expectancy = (data['win'] * data['wins'] - abs(data['loss']) * (data['total'] - data['wins'])) / data['total'] if data['total'] > 0 else 0
        trade_counts = data['total']

        return total_pnl, avg_pnl, avg_win, avg_loss, win_rates, expectancy, trade_counts

    async def getStatsByTime(self, mode:str='daily') -> dict:
        """
        P&L por día de la semana
        
        mode: str
            Can be 'daily', 'hourly', 'monthly' or 'yearly'
        """

        if mode == 'monthly':
            x_axis = 'months'
            time_format = lambda x: str(x.month)
            time_list = list(range(12))
        elif mode == 'yearly':
            x_axis = 'years'
            time_format = lambda x: str(x.year)
            time_list = None
        elif mode == 'hourly':
            x_axis = 'hours'
            time_format = lambda x: f"{x.hour:02d}:00"
            time_list = [f"{h:02d}:00" for h in range(24)]
        elif mode == 'weekday':
            x_axis = 'days'
            days_map = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
            time_format = lambda x: days_map[x.weekday()]
            time_list = [days_map[d] for d in range(7)]
        else:
            x_axis = 'days'
            time_format = lambda x: x.strftime('%Y-%m-%d')
            time_list = None

        if not self.data or not self.pnl_values or len(self.pnl_values) <= 0:
            return {x_axis: [], 'total_pnl': [], 'avg_pnl': [], 'avg_win': [], 'avg_loss': [], 'win_rate': [], 'expectancy': [], 'trade_count': []}
        
        stats = defaultdict(lambda: {'pnl': [], 'wins': 0, 'win': 0, 'loss': 0, 'total': 0})
        
        for i, d in enumerate(self.data):
            time_val = time_format(d['entry_date'])
            stats[time_val] = self._getStatRequirements(prev=stats[time_val], pnl=self.pnl_values[i])
        
        times_list = list(stats.keys()) if time_list is None else time_list
        def getKey(key, iterable, dictionary):
            formated = key if isinstance(key, type(iterable[0])) else type(iterable[0])(key)
            return self._calculateStats(dictionary[formated]) if formated in iterable else (0, 0, 0, 0, 0, 0, 0)
        
        (total_pnl, avg_pnl, avg_win, avg_loss, win_rates, expectancy, trade_counts) = \
            zip(*[getKey(time_val, list(stats.keys()), stats) for time_val in times_list])

        return {
            x_axis: times_list,
            'total_pnl': list(total_pnl),
            'avg_pnl': list(avg_pnl),
            'avg_win': list(avg_win),
            'avg_loss': list(avg_loss),
            'win_rate': list(win_rates),
            'expectancy': list(expectancy),
            'trade_count': list(trade_counts),
            'chart_type': 'multi_bar'
        }
    
    async def getStatsBySymbol(self) -> dict:
        """P&L por símbolo (top N)"""
        if not self.data or not self.pnl_values or len(self.pnl_values) <= 0:
            return {'symbols': [], 'total_pnl': [], 'avg_pnl': [], 'avg_win': [], 'avg_loss': [], 'win_rate': [], 'expectancy': [], 'trade_count': []}
        
        stats = defaultdict(lambda: {'pnl': [], 'wins': 0, 'win': 0, 'loss': 0, 'total': 0})
        
        for i, d in enumerate(self.data):
            stats[d['symbol']] = self._getStatRequirements(stats[d['symbol']], pnl=self.pnl_values[i])
        
        sorted_data = sorted(
            [(symbol,) + self._calculateStats(stat) for symbol, stat in stats.items()],
            key=lambda x: x[1],  # x[1] es total_pnl
            reverse=True  # De mayor a menor
        )

        # Desempaquetar de vuelta a listas separadas
        symbols, total_pnl, avg_pnl, avg_win, avg_loss, win_rates, expectancy, trade_counts = zip(*sorted_data)
        
        return {
            'symbols': list(symbols),
            'total_pnl': list(total_pnl),
            'avg_pnl': list(avg_pnl),
            'avg_win': list(avg_win),
            'avg_loss': list(avg_loss),
            'win_rate': list(win_rates),
            'expectancy': list(expectancy),
            'trade_count': list(trade_counts),
            'chart_type': 'multi_bar'
        }
    
    async def getHoldTimeAnalysis(self) -> dict:
        """Análisis de tiempo de mantenimiento vs P&L"""
        
        if not self.data or not self.pnl_values or len(self.pnl_values) <= 0:
            return {'hold_times': [], 'pnl': [], 'colors': []}
        
        def getHoldTimeMinutes(d:dict):
            if 'exit_date' in d and 'entry_date' in d and d['entry_date']:
                exit_date = d['exit_date'] or (datetime.now() if isinstance(d['entry_date'], datetime) else date.today())
                return (exit_date - d['entry_date']).total_seconds() / 60
            return 0
        
        hold_times = []
        colors = []
        
        for i, d in enumerate(self.data):
            hold_time = getHoldTimeMinutes(d)
            if hold_time > 0:  # Solo incluir trades con tiempo válido
                hold_times.append(hold_time)
                colors.append('green' if self.pnl_values[i] > 0 else 'red' if self.pnl_values[i] < 0 else 'gray')
        
        return {
            'hold_times': hold_times,
            'pnl': self.pnl_values,
            'colors': colors,
            'chart_type': 'scatter'
        }
    
    async def getStreaks(self) -> dict:
        """Gráfico de rachas consecutivas"""
        if not self.pnl_values:
            return {'streaks': [], 'types': []}
        
        streaks = []
        current_streak = 0
        current_type = None
        
        for pnl in self.pnl_values:
            if pnl > 0:  # Win
                if current_type == 'win':
                    current_streak += 1
                else:
                    if current_streak > 0:
                        streaks.append({'length': current_streak, 'type': current_type})
                    current_streak = 1
                    current_type = 'win'
            elif pnl < 0:  # Loss
                if current_type == 'loss':
                    current_streak += 1
                else:
                    if current_streak > 0:
                        streaks.append({'length': current_streak, 'type': current_type})
                    current_streak = 1
                    current_type = 'loss'
            else:  # Scratch - reset streak
                if current_streak > 0:
                    streaks.append({'length': current_streak, 'type': current_type})
                current_streak = 0
                current_type = None
        
        # Añadir última racha si existe
        if current_streak > 0:
            streaks.append({'length': current_streak, 'type': current_type})
        
        return {
            'streaks': [s['length'] for s in streaks],
            'types': [s['type'] for s in streaks],
            'chart_type': 'streak_bar'
        }
    
    async def getSizeAnalysis(self) -> dict:
        """Análisis de tamaño de posición vs P&L"""
        if not self.data or not self.pnl_values or len(self.pnl_values) <= 0:
            return {'sizes': [], 'pnl': [], 'colors': []}
        
        sizes = []
        colors = []
        
        for i, d in enumerate(self.data):
            if 'exit_quantity' in d and d['exit_quantity']:
                sizes.append(d['exit_quantity'])
                colors.append('green' if self.pnl_values[i] > 0 else 'red' if self.pnl_values[i] < 0 else 'gray')
        
        return {
            'sizes': sizes,
            'pnl': self.pnl_values,
            'colors': colors,
            'chart_type': 'scatter'
        }

    async def getAll(self):
        """Obtener todos los gráficos de una vez"""
        equity_curve, daily_pnl, monthly_pnl, pnl_distribution, hour_analysis, day_analysis, weekday_analysis, month_analysis, year_analysis, symbol_performance, hold_time_analysis, size_analysis = \
        await asyncio.gather(
            self.getEquityCurve(),
            self.getPnlTimeHistogram(mode='daily'),
            self.getPnlTimeHistogram(mode='monthly'),
            self.getPnlDistribution(),
            self.getStatsByTime(mode='hourly'),
            self.getStatsByTime(mode='daily'),
            self.getStatsByTime(mode='weekday'),
            self.getStatsByTime(mode='monthly'),
            self.getStatsByTime(mode='yearly'),
            self.getStatsBySymbol(),
            self.getHoldTimeAnalysis(),
            self.getSizeAnalysis()
        )
        return {
            'equity_curve': equity_curve,
            'daily_pnl': daily_pnl,
            'monthly_pnl': monthly_pnl,
            'pnl_distribution': pnl_distribution,
            'hour_analysis': hour_analysis,
            'day_analysis': day_analysis,
            'weekday_analysis': weekday_analysis,
            'month_analysis': month_analysis,
            'year_analysis': year_analysis,
            'symbol_performance': symbol_performance,
            'hold_time_analysis': hold_time_analysis,
            # 'streaks': self.getStreaks(),
            'size_analysis': size_analysis
        }
        
    def to_json(self, charts:dict=None):
        """Convertir todos los gráficos a JSON para enviar al frontend"""
        return json.dumps(self.getAll() if charts is None else charts, default=str)  # default=str para manejar objetos datetime

class TradePerformance:

    def __init__(self, data: list[Trade], gross:bool=False, exclude:list[str]=['strategy', 'media', 'errors', 'conditions', 'transactions']) -> None:
        self.date_format = '%Y-%m-%d'
        self.time_format = '%H:%M:%S'
        new_data = self.processData(data=data, exclude=exclude)
        self.stats = Stats(data=new_data, gross=gross)
        self.charts = Charts(data=new_data, gross=gross)
        # super().__init__(data=self.processData(data=data, exclude=exclude), gross=gross)
        self.date_format = '%Y-%m-%d'
        self.time_format = '%H:%M:%S'

    ## PROCESSING
    def getCandles(self, data:list[Trade]):
        
        start_date = min(e.entry_date for e in data)
        end_date = max(e.exit_date or datetime.now().date() for e in data)

        return Candle.query.filter(
            Candle.symbol.in_([e.symbol for e in data]),
            Candle.date >= datetime.combine(start_date, datetime.min.time()),
            Candle.date <= datetime.combine(end_date, datetime.max.time()),
            Candle.timeframe == '1m'
        ).order_by(Candle.symbol, Candle.date.asc()).all()

    def processData(self, data:list[Trade], exclude:list[dict]=[]) -> list[dict]:
        if len(data) > 0 and isinstance(data[0], Trade):
            all_candles: list[Candle] = self.getCandles(data=data)
            return [{**d.to_dict(exclude=exclude),
                     **{'side': d.trade_type.upper() == 'LONG', 
                        'entry_date': datetime.combine(d.entry_date, datetime.strptime(d.entry_time, self.time_format).time() or datetime.min.time()),
                        'exit_date': datetime.combine(d.exit_date, datetime.strptime(d.exit_time, self.time_format).time() or datetime.min.time()),
                        'candles': [c.to_dict() for c in all_candles
                                    if c.symbol == d.symbol and d.entry_date <= c.date.date() <= (d.exit_date or (datetime.now() if isinstance(d.entry_date, datetime) else date.today()))]
                        }
                    } for d in data]
        else:
            return data

    ## STATS
    async def getStats(self, gross:bool=None):
        """Calcular todas las estadísticas de performance"""
        if self.stats.data is None or len(self.stats.data) == 0:
            return await self.stats.getEmpty()

        if gross is not None:
            self.gross = gross

        total_trades = len(self.stats.data)
        
        # Extraer datos básicos
        volumes = [d.get('exit_quantity', 0) for d in self.stats.data]
        commissions = [d.get('commission', 0) for d in self.stats.data]
        fees = [d.get('fees', 0) for d in self.stats.data]
        total_commissions = sum(commissions)
        total_fees = sum(fees)

        pnl_values = [(d['profit_loss'] + d['commission'] if self.stats.gross else d['profit_loss']) for d in self.stats.data]
        hold_times, mfe_mae_stats, stats = await asyncio.gather(
            self.stats.calculateHoldTimes(),
            self.stats.calculateMaximumExecutions(),
            self.stats.getStats(values=pnl_values)
        )
        
        # ===== COMPILAR RESULTADO =====
        return {**stats, 
            **{
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
        }

    ## CHARTS
    async def tradesEvolution(self) -> dict:
        
        # PROCESAMIENTO DE EQUITY CURVES
        equities = {
            d['symbol'] + '_' + str(d['id']): {
                'data': d['equity'], 
                'date': d['entry_date'],
                'symbol': d['symbol'],
                'trade_id': d['id']
            } 
            for d in self.charts.data
        }
        
        # Preparar datos para el gráfico de líneas de evolución de trades
        max_len = max(len(v['data']) for v in equities.values()) if equities else 0
        
        # Datos para Chart.js - Evolución de trades
        trades_evolution_data = {
            'labels': list(range(max_len)),  # X axis (puntos temporales)
            'datasets': []
        }
        
        # Colores para las líneas
        colors = [
            'rgb(255, 99, 132)', 'rgb(54, 162, 235)', 'rgb(255, 205, 86)',
            'rgb(75, 192, 192)', 'rgb(153, 102, 255)', 'rgb(255, 159, 64)'
        ]
        
        for i, (trade_key, equity_data) in enumerate(equities.items()):
            # Rellenar con null para mantener longitud consistente
            padded_data = equity_data['data'] + [None] * (max_len - len(equity_data['data']))
            
            trades_evolution_data['datasets'].append({
                'label': f"{equity_data['symbol']} (ID: {equity_data['trade_id']})",
                'data': padded_data,
                'borderColor': colors[i % len(colors)],
                'backgroundColor': colors[i % len(colors)] + '20',  # Transparencia
                'fill': False,
                'tension': 0.1
            })
        
        return {
            'trades_evolution': trades_evolution_data,
            'success': True
        }

    async def tradeSpeed(self) -> dict:
        """
        Procesa los trades y prepara los datos para Chart.js
        """
        
        # PROCESAMIENTO DE EQUITY CURVES
        equities = {
            d['symbol'] + '_' + str(d['id']): {
                'data': d['equity'], 
                'date': d['entry_date'],
                'symbol': d['symbol'],
                'trade_id': d['id']
            } 
            for d in self.charts.data
        }
        
        # Preparar datos para el gráfico de líneas de evolución de trades
        max_len = max(len(v['data']) for v in equities.values()) if equities else 0
        
        # ANÁLISIS DE PATRONES DE ENTRADA
        curves: pd.DataFrame = pd.DataFrame({
            k: v['data'] + [np.nan]*(max_len - len(v['data'])) 
            for k, v in equities.items()
        }) if equities else pd.DataFrame()
        
        # Clasificación de patrones
        straight_up = []
        straight_dn = []
        finish_up = []
        finish_dn = []
        
        if not curves.empty:
            for c in curves.columns:
                series = curves[c].dropna()
                if len(series) == 0:
                    continue
                    
                min_idx = series.idxmin()
                max_idx = series.idxmax()
                entry = series.iloc[0]
                
                trade_info = {'symbol': c, 'date': equities[c]['date']}
                
                if min_idx < max_idx and series.iloc[min_idx] < entry and entry < series.iloc[max_idx]:
                    finish_up.append(trade_info)
                elif min_idx < max_idx and series.iloc[min_idx] == entry and entry < series.iloc[max_idx]:
                    straight_up.append(trade_info)
                elif max_idx < min_idx and series.iloc[min_idx] < entry and entry < series.iloc[max_idx]:
                    finish_dn.append(trade_info)
                elif max_idx < min_idx and series.iloc[max_idx] == entry and entry > series.iloc[min_idx]:
                    straight_dn.append(trade_info)
        
        # Contar patrones por fecha
        bar_data = {'straight_up': {}, 'straight_dn': {}, 'finish_up': {}, 'finish_dn': {}}
        
        for pattern_list, pattern_name in [
            (straight_up, 'straight_up'), (straight_dn, 'straight_dn'),
            (finish_up, 'finish_up'), (finish_dn, 'finish_dn')
        ]:
            for trade_info in pattern_list:
                date_str = trade_info['date'].strftime('%Y-%m-%d') if hasattr(trade_info['date'], 'strftime') else str(trade_info['date'])
                bar_data[pattern_name][date_str] = bar_data[pattern_name].get(date_str, 0) + 1
        
        # Crear DataFrame y aplicar rolling window
        bar_df = pd.DataFrame(bar_data).fillna(0).sort_index()
        
        if not bar_df.empty:
            # Rolling sum de 5 períodos
            bar_df_rolling = bar_df.rolling(5, min_periods=1).sum()
            
            # Calcular porcentajes
            row_sums = bar_df_rolling.sum(axis=1)
            bar_df_pct = bar_df_rolling.div(row_sums, axis=0).fillna(0) * 100
        else:
            bar_df_rolling = pd.DataFrame()
            bar_df_pct = pd.DataFrame()
        
        # Preparar datos para Chart.js - Entry Timing Absolutos
        trade_speed_abs_data = {
            'labels': bar_df_rolling.index.tolist() if not bar_df_rolling.empty else [],
            'datasets': {
                'straight_up': bar_df_rolling['straight_up'].tolist() if not bar_df_rolling.empty else [],
                'straight_dn': bar_df_rolling['straight_dn'].tolist() if not bar_df_rolling.empty else [],
                'finish_up': bar_df_rolling['finish_up'].tolist() if not bar_df_rolling.empty else [],
                'finish_dn': bar_df_rolling['finish_dn'].tolist() if not bar_df_rolling.empty else [],
            }
        }
        
        # Preparar datos para Chart.js - Entry Timing Porcentajes
        trade_speed_pct_data = {
            'labels': bar_df_pct.index.tolist() if not bar_df_pct.empty else [],
            'datasets': {
                'straight_up': bar_df_pct['straight_up'].tolist() if not bar_df_pct.empty else [],
                'straight_dn': bar_df_pct['straight_dn'].tolist() if not bar_df_pct.empty else [],
                'finish_up': bar_df_pct['finish_up'].tolist() if not bar_df_pct.empty else [],
                'finish_dn': bar_df_pct['finish_dn'].tolist() if not bar_df_pct.empty else [],
            }
        }
        
        # Estadísticas adicionales
        stats = {
            'total_trades': len(self.charts.data),
            'straight_up_count': len(straight_up),
            'straight_dn_count': len(straight_dn), 
            'finish_up_count': len(finish_up),
            'finish_dn_count': len(finish_dn)
        }
        
        return {
            'trade_speed_abs': trade_speed_abs_data,
            'trade_speed_pct': trade_speed_pct_data,
            'stats': stats,
            'success': True
        }

    async def getCharts(self, gross:bool=None) -> dict:
        """Obtener todos los gráficos de una vez"""
        
        if gross is not None:
            self.gross = gross
            self.charts.getPnl()
        
        equity_curve, daily_pnl, monthly_pnl, pnl_distribution, hour_analysis, day_analysis, weekday_analysis, month_analysis, year_analysis, symbol_performance, hold_time_analysis, size_analysis, trade_speed = \
        await asyncio.gather(
            self.charts.getEquityCurve(),
            self.charts.getPnlTimeHistogram(mode='daily'),
            self.charts.getPnlTimeHistogram(mode='monthly'),
            self.charts.getPnlDistribution(),
            self.charts.getStatsByTime(mode='hourly'),
            self.charts.getStatsByTime(mode='daily'),
            self.charts.getStatsByTime(mode='weekday'),
            self.charts.getStatsByTime(mode='monthly'),
            self.charts.getStatsByTime(mode='yearly'),
            self.charts.getStatsBySymbol(),
            self.charts.getHoldTimeAnalysis(),
            self.charts.getSizeAnalysis(),
            self.tradeSpeed()
        )
        return {
            'equity_curve': equity_curve,
            'daily_pnl': daily_pnl,
            'monthly_pnl': monthly_pnl,
            'pnl_distribution': pnl_distribution,
            'hour_analysis': hour_analysis,
            'day_analysis': day_analysis,
            'weekday_analysis': weekday_analysis,
            'month_analysis': month_analysis,
            'year_analysis': year_analysis,
            'symbol_performance': symbol_performance,
            'hold_time_analysis': hold_time_analysis,
            # 'streaks': self.getStreaks(),
            'size_analysis': size_analysis,
            'trade_speed': trade_speed
        }

class WatchlistPerformance:

    def __init__(self, data: list[WatchlistEntry], gross:bool=False, side:bool=True, exclude:list[str]=['watchlist', 'levels', 'conditions']) -> None:
        self.side: bool = side # True for LONG and False for SHORT
        self.date_format = '%Y-%m-%d %H:%M:%S%z'
        self.time_format = '%H:%M:%S'
        self.gross = gross
        new_data = self.processData(data=data, exclude=exclude)
        self.stats = Stats(data=new_data, gross=gross)
        self.charts = Charts(data=new_data, gross=gross)
        self.date_format = '%Y-%m-%d %H:%M:%S%z'
        self.time_format = '%H:%M:%S'

    ## PROCESSING
    def getCandles(self, data:list[WatchlistEntry]):
        
        start_date = min(e.date for e in data)
        end_date = max(e.date_exit or datetime.now().date() for e in data)

        return Candle.query.filter(
            Candle.symbol.in_([e.symbol for e in data]),
            Candle.date >= datetime.combine(start_date, datetime.min.time()),
            Candle.date <= datetime.combine(end_date, datetime.max.time()),
            Candle.timeframe == '1m'
        ).order_by(Candle.symbol, Candle.date.asc()).all()

    def processData(self, data:list[WatchlistEntry], exclude:list[str]=[]) -> list[dict]:
        
        if len(data) > 0 and isinstance(data[0], WatchlistEntry):
            all_candles: list[Candle] = self.getCandles(data)
            new: list[dict] = []
            for entry in data:
                # candles = [c.to_dict() for c in entry.getCandles(timeframe='1m')]
                candles = [c.to_dict() for c in all_candles
                      if c.symbol == entry.symbol and entry.date <= c.date.date() <= (entry.date_exit or (datetime.now() if isinstance(entry.date, datetime) else date.today()))]
                if len(candles) > 0:
                    n = entry.to_dict(exclude=exclude)
                    n.update({'entry_date': datetime.strptime(candles[0]['date'], self.date_format), 
                              'exit_date': datetime.strptime(candles[-1]['date'], self.date_format),
                            'side': self.side, 'exit_quantity': 1, 'commission': 0, 
                            'candles': candles, 'entry_price': candles[0]['open'],
                            'exit_price': candles[-1]['close']})
                    n['profit_loss'] = n['exit_price'] - n['entry_price'] if self.side else n['entry_price'] - n['exit_price']
                    new.append(n)

            return new
        else:
            return data

    ## STATS

    async def sectorAnalysis(self):
        
        sectors = {}
        for d in self.stats.data:
            if d['sector'] is not None:
                if d['sector'] not in sectors:
                    sectors[d['sector']] = []
                sectors[d['sector']].append((d['profit_loss'] + d['commission']) / d['entry_price'] if self.gross else d['profit_loss'])
        
        return {k: {'avg_return': self.stats.mean(v),
                    'count': len(v)} for k, v in sectors.items()}

    async def getStats(self, gross:bool=None):
        """Calcular todas las estadísticas de performance"""
        if self.stats.data is None or len(self.stats.data) == 0:
            return await self.stats.getEmpty()

        if gross is not None:
            self.stats.gross = gross

        total_trades = len(self.stats.data)
        
        # Extraer datos básicos
        volumes = [d.get('exit_quantity', 0) for d in self.stats.data]
        commissions = [d.get('commission', 0) for d in self.stats.data]
        fees = [d.get('fees', 0) for d in self.stats.data]
        total_commissions = sum(commissions)
        total_fees = sum(fees)

        pnl_values = [((d['profit_loss'] + d['commission']) / d['entry_price'] if self.gross else d['profit_loss']) for d in self.stats.data]
        hold_times, mfe_mae_stats, stats, sector_stats = await asyncio.gather(
            self.stats.calculateHoldTimes(),
            self.stats.calculateMaximumExecutions(),
            self.stats.getStats(values=pnl_values),
            self.sectorAnalysis()
        )
        
        # ===== COMPILAR RESULTADO =====
        return {**stats, 
            **{
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

                'sectors_stats': sector_stats
            }
        }

    ## CHARTS
    def _analyze_breakouts(self) -> dict:
        """Análisis de rupturas de máximos/mínimos"""
        if not self.charts.data:
            return {}
            
        breakout_stats = {
            'high_breaks': 0,
            'low_breaks': 0,
            'total_opportunities': 0
        }
        
        for symbol_data in self.charts.data:
            candles = symbol_data['candles']
            
            if len(candles) < 2:
                continue
                
            for i in range(1, len(candles)):
                prev_high = max(c['high'] for c in candles[:i])
                prev_low = min(c['low'] for c in candles[:i])
                
                current = candles[i]
                
                breakout_stats['total_opportunities'] += 1
                
                if current['high'] > prev_high:
                    breakout_stats['high_breaks'] += 1
                if current['low'] < prev_low:
                    breakout_stats['low_breaks'] += 1
        
        total_ops = breakout_stats['total_opportunities']
        if total_ops > 0:
            breakout_stats['high_break_rate'] = breakout_stats['high_breaks'] / total_ops * 100
            breakout_stats['low_break_rate'] = breakout_stats['low_breaks'] / total_ops * 100
        
        return breakout_stats
    
    async def seriesAnalysis(self, is_daytrading: bool) -> dict:
        """Preparar datos para los gráficos"""
        if not self.charts.data:
            return {}
        
        monte_carlo_data = []
        
        # Normalizar todas las series a partir del precio de entrada (100%)
        max_length = 0
        
        for symbol_data in self.charts.data:
            candles = symbol_data['candles']
            entry_price = symbol_data['entry_price']
            
            if not candles:
                continue
                
            normalized_prices = []
            for i, candle in enumerate(candles):
                normalized_price = (candle['close'] / entry_price) * 100
                
                if is_daytrading:
                    time_point = i * (1/60)  # Minutos a horas
                else:
                    time_point = i  # Días
                    
                normalized_prices.append({
                    'x': time_point,
                    'y': normalized_price,
                    'symbol': symbol_data['symbol']
                })
            
            monte_carlo_data.append(normalized_prices)
            max_length = max(max_length, len(normalized_prices))
        
        # Calcular percentiles y media para cada punto temporal
        percentile_data = {'mean': [], 'p25': [], 'p75': [], 'p10': [], 'p90': []}
        
        for t in range(max_length):
            values_at_t = []
            for series in monte_carlo_data:
                if t < len(series):
                    values_at_t.append(series[t]['y'])
            
            if values_at_t:
                time_val = t * (1/60 if is_daytrading else 1)
                percentile_data['mean'].append({'x': time_val, 'y': np.mean(values_at_t)})
                percentile_data['p25'].append({'x': time_val, 'y': np.percentile(values_at_t, 25)})
                percentile_data['p75'].append({'x': time_val, 'y': np.percentile(values_at_t, 75)})
                percentile_data['p10'].append({'x': time_val, 'y': np.percentile(values_at_t, 10)})
                percentile_data['p90'].append({'x': time_val, 'y': np.percentile(values_at_t, 90)})
    
        return {
            'monte_carlo_traces': monte_carlo_data,
            'percentile_data': percentile_data,
        }
    
    async def optimizationHeatmap(self, is_daytrading: bool) -> list[dict]:
        """Generar datos para el heatmap de probabilidades"""
        if not self.charts.data:
            return []
            
        # Grid para el heatmap
        time_bins = 24 if is_daytrading else 10  # 24 horas o 10 días máximo
        price_bins = 20  # 20 niveles de precio
        
        # Matriz para contar extremos
        high_matrix = np.zeros((price_bins, time_bins))
        low_matrix = np.zeros((price_bins, time_bins))
        total_matrix = np.zeros((price_bins, time_bins))
        
        for symbol_data in self.charts.data:
            candles = symbol_data['candles']
            entry_price = symbol_data['entry_price']
            
            if not candles:
                continue
                
            # Normalizar precios (80% - 120% del precio de entrada)
            price_range = (0.8, 1.2)
            
            for i, candle in enumerate(candles):
                if is_daytrading:
                    time_idx = min(candle['date'].hour, time_bins - 1)
                else:
                    time_idx = min(i, time_bins - 1)
                
                # Normalizar precio
                norm_high = candle['high'] / entry_price
                norm_low = candle['low'] / entry_price
                
                # Convertir a índices de precio
                high_price_idx = int((norm_high - price_range[0]) / (price_range[1] - price_range[0]) * (price_bins - 1))
                low_price_idx = int((norm_low - price_range[0]) / (price_range[1] - price_range[0]) * (price_bins - 1))
                
                # Asegurar que están en rango
                high_price_idx = max(0, min(price_bins - 1, high_price_idx))
                low_price_idx = max(0, min(price_bins - 1, low_price_idx))
                
                # Marcar como extremos si son máximos/mínimos del día o período
                is_period_high = candle['high'] == max(c['high'] for c in candles[max(0, i-5):i+6])  # Ventana de 11 períodos
                is_period_low = candle['low'] == min(c['low'] for c in candles[max(0, i-5):i+6])
                
                if is_period_high:
                    high_matrix[high_price_idx, time_idx] += 1
                if is_period_low:
                    low_matrix[low_price_idx, time_idx] += 1
                    
                total_matrix[high_price_idx, time_idx] += 1
                if high_price_idx != low_price_idx:
                    total_matrix[low_price_idx, time_idx] += 1
        
        # Convertir a probabilidades y formato para el gráfico
        heatmap_data = []
        for price_idx in range(price_bins):
            for time_idx in range(time_bins):
                if total_matrix[price_idx, time_idx] > 0:
                    high_prob = high_matrix[price_idx, time_idx] / total_matrix[price_idx, time_idx]
                    low_prob = low_matrix[price_idx, time_idx] / total_matrix[price_idx, time_idx]
                    
                    # Combinar probabilidades (verde para máximos, rojo para mínimos)
                    combined_prob = high_prob - low_prob  # Rango de -1 a 1
                    
                    price_level = price_range[0] + (price_idx / (price_bins - 1)) * (price_range[1] - price_range[0])
                    
                    heatmap_data.append({
                        'x': time_idx,
                        'y': price_level * 100,  # Convertir a porcentaje
                        'z': combined_prob
                    })
        
        return heatmap_data
    
    async def executionOptimization(self, order: int = 60, max_bins: int = 10):
        """
        Prepara datos para Chart.js incluyendo:
        - Serie de precios
        - Heatmap (máximos / mínimos)
        - Histogramas (precio y tiempo)
        """


        def mark_extrema(df: pd.DataFrame, order: int = 5, of_day:bool=True) -> pd.DataFrame:
            """
            Marca máximos y mínimos locales en la columna 'price'.
            order = cuántos vecinos mirar a cada lado.
            """

            df = df.sort_values(["symbol", "date"]).reset_index(drop=True)
            df["is_max"] = False
            df["is_min"] = False

            if of_day:
                for symbol, subdf in df.groupby("symbol", group_keys=False):
                    roll_max = subdf["price"].idxmax()
                    roll_min = subdf["price"].idxmin()

                    is_max = subdf["price"] == roll_max
                    is_min = subdf["price"] == roll_min

                    df.loc[roll_max, "is_max"] = True
                    df.loc[roll_min, "is_min"] = True
            else:
                window = 2 * order + 1
                for symbol, subdf in df.groupby("symbol", group_keys=False):
                    roll_max = subdf["price"].rolling(window, center=True).max()
                    roll_min = subdf["price"].rolling(window, center=True).min()

                    is_max = subdf["price"] == roll_max
                    is_min = subdf["price"] == roll_min

                    df.loc[is_max.index, "is_max"] |= is_max
                    df.loc[is_min.index, "is_min"] |= is_min

            return df
        
        # Data to df
        all_rows = [{
                    "date": pd.to_datetime(c["date"]),
                    "symbol": c["symbol"],
                    "open": c["open"],
                    "high": c["high"],
                    "low": c["low"],
                    "close": c["close"],
                    "volume": c["volume"],
                } for data in self.charts.data for c in data['candles']]
        df = pd.DataFrame(all_rows)
        df = df.sort_values(['symbol', 'date']).copy()
        df['price'] = df.groupby('symbol')['close'].pct_change()
        df['price'] = df.groupby('symbol')['price'].cumsum()
        df.dropna(inplace=True)
        df['index'] = df.groupby('symbol').cumcount()
        df = mark_extrema(df, order=order, of_day=True)
        # df.to_json('datos.json', orient='records', indent=4)

        extrema = df[df["is_max"] | df["is_min"]].copy()
        if extrema.empty:
            return None  # no hay máximos ni mínimos
        
        # Datasets de precios por activo
        labels = df["index"].copy().unique().tolist()
        datasets = [{
                "label": symbol,
                "data": subdf.sort_values("index")["price"].tolist(),
            } for symbol, subdf in df.groupby("symbol")]

        # Heatmap global
        agg = Agrupations(extrema)
        max_heatmap_df, min_heatmap_df = agg.bins(max_bins=max_bins, min_bins=50)
        print(agg.dbscan(max_distance=0.2, min_samples=2))
        
        heatmap_max = [
            {"x_bin": i, "y_bin": float(c), "count": float(max_heatmap_df.loc[i, c])}
            for i in max_heatmap_df.index for c in max_heatmap_df.columns
            if max_heatmap_df.loc[i, c] != 0
        ]
        heatmap_min = [
            {"x_bin": i, "y_bin": float(c), "count": float(min_heatmap_df.loc[i, c])}
            for i in min_heatmap_df.index for c in min_heatmap_df.columns
            if min_heatmap_df.loc[i, c] != 0
        ]

        # Price Histogram
        hist_price_max = max_heatmap_df.sum(axis=0)
        hist_price_max = hist_price_max[hist_price_max != 0]
        hist_price_max_labels = hist_price_max.index.tolist()
        hist_price_max_data = hist_price_max.tolist()
        
        hist_price_min = min_heatmap_df.sum(axis=0)
        hist_price_min = hist_price_min[hist_price_min != 0]
        hist_price_min_labels = hist_price_min.index.tolist()
        hist_price_min_data = hist_price_min.tolist()

        # Histograma superior (tiempo)
        hist_time_max = max_heatmap_df.sum(axis=1)
        hist_time_max = hist_time_max[hist_time_max != 0]
        hist_time_max_labels = hist_time_max.index.tolist()
        hist_time_max_data = hist_time_max.tolist()
        
        hist_time_min = min_heatmap_df.sum(axis=1)
        hist_time_min = hist_time_min[hist_time_min != 0]
        hist_time_min_labels = hist_time_min.index.tolist()
        hist_time_min_data = hist_time_min.tolist()

        return {
            "line": {
                "labels": labels,
                "datasets": datasets,
            },
            "heatmap_max": heatmap_max,
            "heatmap_min": heatmap_min,
            "hist_price_max": {
                "labels": hist_price_max_labels,
                "data": hist_price_max_data,
            },
            "hist_price_min": {
                "labels": hist_price_min_labels,
                "data": hist_price_min_data,
            },
            "hist_time_max": {
                "labels": hist_time_max_labels,
                "data": hist_time_max_data,
            },
            "hist_time_min": {
                "labels": hist_time_min_labels,
                "data": hist_time_min_data,
            },
        }


    async def getCharts(self, gross:bool=None) -> dict:
        """Obtener todos los gráficos de una vez"""

        if gross is not None:
            self.charts.gross = gross
            self.charts.getPnl()
            
        equity_curve, daily_pnl, monthly_pnl, pnl_distribution, hour_analysis, day_analysis, weekday_analysis, month_analysis, year_analysis, symbol_performance, hold_time_analysis, size_analysis, execution_heatmap, series_analysis, execution_optimization = \
        await asyncio.gather(
            self.charts.getEquityCurve(),
            self.charts.getPnlTimeHistogram(mode='daily'),
            self.charts.getPnlTimeHistogram(mode='monthly'),
            self.charts.getPnlDistribution(),
            self.charts.getStatsByTime(mode='hourly'),
            self.charts.getStatsByTime(mode='daily'),
            self.charts.getStatsByTime(mode='weekday'),
            self.charts.getStatsByTime(mode='monthly'),
            self.charts.getStatsByTime(mode='yearly'),
            self.charts.getStatsBySymbol(),
            self.charts.getHoldTimeAnalysis(),
            self.charts.getSizeAnalysis(),
            self.optimizationHeatmap(is_daytrading=False), # TODO: How do I automatically detect if use daytrading or not?
            self.seriesAnalysis(is_daytrading=False),
            self.executionOptimization(order=5, max_bins=50)
        )
        return {
            'equity_curve': equity_curve,
            'daily_pnl': daily_pnl,
            'monthly_pnl': monthly_pnl,
            'pnl_distribution': pnl_distribution,
            'hour_analysis': hour_analysis,
            'day_analysis': day_analysis,
            'weekday_analysis': weekday_analysis,
            'month_analysis': month_analysis,
            'year_analysis': year_analysis,
            'symbol_performance': symbol_performance,
            'hold_time_analysis': hold_time_analysis,
            # 'streaks': self.getStreaks(),
            'size_analysis': size_analysis,
            'monte_carlo_traces': series_analysis['monte_carlo_traces'],
            'percentile_data': series_analysis['percentile_data'],
            'heatmap_data': execution_heatmap,
            'execution_optimization': execution_optimization
        }



class WatchlistPerformanceMetrics:

    def __init__(self, entries:list[WatchlistEntry]):
        self.entries: list[WatchlistEntry] = entries

    def mean(self, numbers):
        return float(np.mean([n for n in numbers if n is not None])) if (isinstance(numbers, pd.Series) and not numbers.empty) or numbers else None
    
    def median(self, numbers):
        return float(np.median([n for n in numbers if n is not None])) if (isinstance(numbers, pd.Series) and not numbers.empty) or numbers else None
    
    def std(self, numbers):
        return float(np.std([n for n in numbers if n is not None])) if (isinstance(numbers, pd.Series) and not numbers.empty) or numbers else None
    
    def max(self, numbers):
        return float(np.max([n for n in numbers if n is not None])) if (isinstance(numbers, pd.Series) and not numbers.empty) or numbers else None
    
    def min(self, numbers):
        return float(np.min([n for n in numbers if n is not None])) if (isinstance(numbers, pd.Series) and not numbers.empty) or numbers else None

    def dfGetValue(self, col:str, idx:int, df:pd.DataFrame, default=None, type=float):
        try:
            return type(df[col].iloc[idx]) if col in df.columns else default
        except KeyError:
            print('Key error accessing column:', col, ' with index: ', idx)
            return default

    def analyze_entry_performance(self, entry: WatchlistEntry):
        """Analiza el rendimiento de una entrada individual"""
        
        # Determinar fechas de análisis
        start_date = entry.date
        end_date = entry.date_exit or datetime.now().date()
        
        if start_date >= end_date:
            return None
        
        # Obtener datos de velas para el símbolo
        candles: list[Candle] = Candle.query.filter(
            and_(
                Candle.symbol == entry.symbol,
                Candle.date >= start_date,
                Candle.date <= end_date,
                Candle.timeframe == '1d'  # TODO: Use the 1 minute timeframe for analysis too, how do we define when to download the 1 minute data?
            )
        ).distinct().order_by(Candle.date.asc()).all()
        
        candles_data = pd.DataFrame([c.to_dict() for c in candles])
        if candles_data.empty:
            print('No candles for the watchlist entry:')
            return {
                'symbol': entry.symbol,
                'company_name': entry.company_name,
                'entry_date': start_date.isoformat(),
                'exit_date': end_date.isoformat(),
                'days_held': (end_date - start_date).days,
                'entry_price': entry.price,
                'final_price': None,
                'total_return': None,
                'max_return': None,
                'min_return': None,
                'volatility': None,
                'sector': entry.sector,
                'industry': entry.industry,
                'market_cap': entry.market_cap,
                'score': entry.score,
                'movement_times': {},
                'is_profitable': None
            }
        candles_data[['open', 'high', 'low', 'close', 'volume']] = candles_data[['open', 'high', 'low', 'close', 'volume']].astype(float).map(float)
        # Calcular métricas de rendimiento
        entry_price = entry.price or self.dfGetValue('close', 0, candles_data)  # close del primer candle
        final_price = self.dfGetValue('close', -1, candles_data)  # close del último candle
        
        # Calcular retorno
        total_return = ((final_price - entry_price) / entry_price) * 100
        
        # Encontrar máximo y mínimo durante el período
        max_price = float(candles_data['high'].max())  # high
        min_price = float(candles_data['low'].min())  # low
        
        max_return = ((max_price - entry_price) / entry_price) * 100
        min_return = ((min_price - entry_price) / entry_price) * 100
        
        # Análisis de tiempo de movimientos significativos
        movement_times = self.analyze_movement_timing(candles_data, entry_price)
        
        # Calcular volatilidad
        returns = candles_data['close'].pct_change().dropna()
        volatility = self.std(returns) if not returns.empty else 0
        
        return {
            'symbol': entry.symbol,
            'company_name': entry.company_name,
            'entry_date': start_date.isoformat(),
            'exit_date': end_date.isoformat(),
            'days_held': (end_date - start_date).days,
            'entry_price': entry_price,
            'final_price': final_price,
            'total_return': round(total_return, 2),
            'max_return': round(max_return, 2),
            'min_return': round(min_return, 2),
            'volatility': round(volatility, 2),
            'sector': entry.sector,
            'industry': entry.industry,
            'market_cap': entry.market_cap,
            'score': entry.score,
            'movement_times': movement_times,
            'is_profitable': total_return > 0
        }
        
    def analyze_movement_timing(self, candles_data:pd.DataFrame, entry_price):
        """Analiza los horarios de movimientos significativos"""
        movement_threshold = 0.02  # 2% de movimiento significativo
        
        significant_moves = []
        for i, date, symbol, open_p, high, low, close, volume, session, timeframe, created in candles_data.values:
            timestamp = datetime.strptime(date, '%Y-%m-%d %H:%M:%S%z')
            hour = timestamp.hour
            
            # Calcular movimiento desde precio de entrada
            high_move = ((high - entry_price) / entry_price)
            low_move = ((low - entry_price) / entry_price)
            
            if abs(high_move) >= movement_threshold or abs(low_move) >= movement_threshold:
                significant_moves.append({
                    'hour': hour,
                    'high_move': high_move,
                    'low_move': low_move,
                    'timestamp': timestamp.isoformat()
                })
        
        # Agrupar por horas
        hourly_movements = defaultdict(list)
        for move in significant_moves:
            hourly_movements[move['hour']].append(move)
        
        return dict(hourly_movements)

    def calculate_aggregate_statistics(self, performance_data):
        """Calcula estadísticas agregadas de toda la watchlist"""
        if not performance_data:
            return {}
        
        total_returns = [p['total_return'] for p in performance_data]
        max_returns = [p['max_return'] for p in performance_data]
        min_returns = [p['min_return'] for p in performance_data]
        
        profitable_trades = [p for p in performance_data if p['is_profitable']]
        losing_trades = [p for p in performance_data if not p['is_profitable']]
        
        # Análisis de horarios de movimientos
        all_movement_times = []
        for p in performance_data:
            for hour, moves in p['movement_times'].items():
                all_movement_times.extend([hour] * len(moves))
        
        # Encontrar horas más activas
        hour_counts = defaultdict(int)
        for hour in all_movement_times:
            hour_counts[hour] += 1
        
        most_active_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Análisis por sectores
        sector_performance = defaultdict(list)
        for p in performance_data:
            if p['sector']:
                sector_performance[p['sector']].append(p['total_return'])
        
        sector_stats = {}
        for sector, returns in sector_performance.items():
            sector_stats[sector] = {
                'avg_return': round(self.mean(returns), 2),
                'count': len(returns),
                'win_rate': len([r for r in returns if r > 0]) / len(returns) * 100
            }
        
        return {
            'total_trades': len(performance_data),
            'profitable_trades': len(profitable_trades),
            'losing_trades': len(losing_trades),
            'win_rate': round((len(profitable_trades) / len(performance_data)) * 100, 2),
            'average_return': round(self.mean(total_returns), 2),
            'median_return': round(self.median(total_returns), 2),
            'max_single_return': round(self.max(total_returns), 2),
            'min_single_return': round(self.min(total_returns), 2),
            'average_max_return': round(self.mean(max_returns), 2),
            'average_min_return': round(self.mean(min_returns), 2),
            'std_deviation': round(self.std(total_returns), 2),
            'sharpe_ratio': self.calculate_sharpe_ratio(total_returns),
            'most_active_hours': most_active_hours,
            'sector_performance': sector_stats,
            'bias_direction': 'BULLISH' if self.mean(total_returns) > 0 else 'BEARISH'
        }

    def calculate_sharpe_ratio(self, returns):
        """Calcula el ratio de Sharpe asumiendo tasa libre de riesgo del 2%"""
        if not returns or self.std(returns) == 0:
            return 0
        
        risk_free_rate = 2.0  # 2% anualizado
        excess_returns = self.mean(returns) - risk_free_rate
        return round(excess_returns / self.std(returns), 2)

    def generate_visualization_data(self, performance_data):
        """Genera datos para las visualizaciones"""
        if not performance_data:
            return {}
        
        # Datos para gráfico de retornos
        returns_distribution = [p['total_return'] for p in performance_data]
        
        # Datos para timeline de rendimiento
        timeline_data = []
        for p in performance_data:
            timeline_data.append({
                'date': p['entry_date'],
                'return': p['total_return'],
                'symbol': p['symbol']
            })
        
        timeline_data.sort(key=lambda x: x['date'])
        
        # Datos para análisis de horarios
        hourly_activity = defaultdict(int)
        for p in performance_data:
            for hour, moves in p['movement_times'].items():
                hourly_activity[hour] += len(moves)
        
        hours_data = [{'hour': f"{h:02d}:00", 'activity': count} 
                    for h, count in sorted(hourly_activity.items())]
        
        # Datos para scatter plot de riesgo vs retorno
        risk_return_data = [{
            'symbol': p['symbol'],
            'return': p['total_return'],
            'volatility': p['volatility'],
            'market_cap': p['market_cap'] or 0
        } for p in performance_data]
        
        return {
            'returns_distribution': returns_distribution,
            'timeline': timeline_data,
            'hourly_activity': hours_data,
            'risk_return_scatter': risk_return_data
        }
    
    def getAll(self):
        
        performance_data = []
        for entry in self.entries:
            perf_data = self.analyze_entry_performance(entry)
            if perf_data:
                performance_data.append(perf_data)

        stats = self.calculate_aggregate_statistics(performance_data)
        
        # Generar datos para visualizaciones
        visualizations = self.generate_visualization_data(performance_data)

        return {
            'total_entries': len(self.entries),
            'analyzed_entries': len(performance_data),
            'statistics': stats,
            'visualizations': visualizations,
            'raw_data': performance_data
        }

    def to_json(self):
        """Convertir todos los gráficos a JSON para enviar al frontend"""
        data = self.getAll()
        return json.dumps(data, default=str)  # default=str para manejar objetos datetime
    

from typing import Any
import json

class WatchlistAnalyzer:

    def __init__(self, entries: list[WatchlistEntry], watchlist:Watchlist):
        self.entries = entries
        self.watchlist = watchlist
        self.candles_data = {}
        self.is_daytrading = self.watchlist.type.upper() == 'DAY' or self.watchlist.type.upper() == 'SCALP'
        
    def analyze(self) -> dict[str, Any]:
        """Método principal que ejecuta todo el análisis"""
        # Cargar datos
        self._load_candles_data()
        
        # Determinar si es daytrading o swing/investment
        time_unit = 'hours' if self.is_daytrading else 'days'
        
        # Calcular estadísticas
        stats = {
            'watchlist_info': self._get_watchlist_info(),
            'general_stats': self._calculate_general_stats(self.is_daytrading),
            'time_analysis': self._analyze_time_patterns(self.is_daytrading),
            'performance_stats': self._calculate_performance_stats(),
            'volatility_analysis': self._calculate_volatility_stats(),
            'breakout_analysis': self._analyze_breakouts(),
            'chart_data': self._prepare_chart_data(self.is_daytrading),
            'time_unit': time_unit,
            'is_daytrading': self.is_daytrading
        }
        
        return stats
    
    def _load_candles_data(self):
        """Cargar datos de velas para todos los símbolos"""
        
        for entry in self.entries:
            start_date = entry.date
            end_date = entry.date_exit or datetime.now().date()
            
            if start_date >= end_date:
                return None
                
            # Determinar timeframe según tipo de watchlist
            timeframe = '1m' if self.watchlist.type.upper() in ['SCALP', 'DAY'] else '1d'
            print(f'Loading candles for {entry.symbol} from {entry.date} to {entry.date_exit} with timeframe {timeframe}')
            candles = Candle.query.filter(
                and_(
                    Candle.symbol == entry.symbol,
                    Candle.timeframe == timeframe,
                    Candle.date >= start_date,
                    Candle.date <= end_date
                )
            ).distinct().order_by(Candle.date.asc()).all()
            
            if candles:
                self.candles_data[entry.symbol] = {
                    'entry': entry,
                    'candles': candles,
                    'entry_price': entry.price,
                    'days_in_watchlist': (end_date - start_date).days
                }
    
    def _get_watchlist_info(self) -> dict[str, Any]:
        """Información básica de la watchlist"""
        return {
            'name': self.watchlist.name,
            'type': self.watchlist.type,
            'description': self.watchlist.description,
            'total_entries': len(self.entries),
            'entries_with_data': len(self.candles_data)
        }
    
    def _calculate_general_stats(self, is_daytrading: bool) -> dict[str, Any]:
        """Estadísticas generales de rendimiento"""
        if not self.candles_data:
            return {}
            
        returns = []
        holding_periods = []
        
        for symbol_data in self.candles_data.values():
            candles = symbol_data['candles']
            entry_price = symbol_data['entry_price']
            
            if not candles:
                continue
                
            # Calcular retorno desde precio de entrada hasta último precio
            final_price = candles[-1].close
            return_pct = (final_price - entry_price) / entry_price * 100
            returns.append(return_pct)
            
            # Período de tenencia
            if is_daytrading:
                hours = len(candles) * (1/60)  # Asumiendo 1min candles
                holding_periods.append(hours)
            else:
                days = (candles[-1].date.date() - candles[0].date.date()).days
                holding_periods.append(max(1, days))
        
        if not returns:
            return {}
            
        return {
            'total_trades': len(returns),
            'avg_return': np.mean(returns),
            'median_return': np.median(returns),
            'std_return': np.std(returns),
            'min_return': np.min(returns),
            'max_return': np.max(returns),
            'positive_trades': len([r for r in returns if r > 0]),
            'negative_trades': len([r for r in returns if r < 0]),
            'win_rate': len([r for r in returns if r > 0]) / len(returns) * 100,
            'avg_holding_period': np.mean(holding_periods),
            'mathematical_expectation': np.mean(returns)
        }
    
    def _analyze_time_patterns(self, is_daytrading: bool) -> dict[str, Any]:
        """Análisis de patrones temporales para máximos y mínimos"""
        if not self.candles_data:
            return {}
            
        if is_daytrading:
            return self._analyze_hourly_patterns()
        else:
            return self._analyze_daily_patterns()
    
    def _analyze_hourly_patterns(self) -> dict[str, Any]:
        """Análisis por horas del día para daytrading"""
        high_hours = []
        low_hours = []
        
        for symbol_data in self.candles_data.values():
            candles = symbol_data['candles']
            
            if len(candles) < 2:
                continue
                
            # Encontrar máximos y mínimos locales por día
            df = pd.DataFrame([{
                'hour': c.date.hour,
                'high': c.high,
                'low': c.low,
                'date': c.date.date()
            } for c in candles])
            
            # Agrupar por día y encontrar máximos/mínimos diarios
            daily_extremes = df.groupby('date').agg({
                'high': 'max',
                'low': 'min'
            })
            
            # Para cada día, encontrar la hora del máximo y mínimo
            for date in daily_extremes.index:
                day_data = df[df['date'] == date]
                
                max_hour = day_data[day_data['high'] == daily_extremes.loc[date, 'high']]['hour'].iloc[0]
                min_hour = day_data[day_data['low'] == daily_extremes.loc[date, 'low']]['hour'].iloc[0]
                
                high_hours.append(max_hour)
                low_hours.append(min_hour)
        
        # Calcular distribución por horas
        hour_high_dist = {}
        hour_low_dist = {}
        
        for h in range(24):
            hour_high_dist[str(h)] = high_hours.count(h)
            hour_low_dist[str(h)] = low_hours.count(h)
            
        return {
            'most_common_high_hour': max(hour_high_dist.items(), key=lambda x: x[1])[0] if high_hours else None,
            'most_common_low_hour': max(hour_low_dist.items(), key=lambda x: x[1])[0] if low_hours else None,
            'hourly_high_distribution': hour_high_dist,
            'hourly_low_distribution': hour_low_dist,
            'total_days_analyzed': len(set([c.date.date() for data in self.candles_data.values() for c in data['candles']]))
        }
    
    def _analyze_daily_patterns(self) -> dict[str, Any]:
        """Análisis por días para swing trading"""
        high_days = []
        low_days = []
        
        for symbol_data in self.candles_data.values():
            candles = symbol_data['candles']
            entry_date = symbol_data['entry'].date
            
            if len(candles) < 2:
                continue
                
            max_price = max(c.high for c in candles)
            min_price = min(c.low for c in candles)
            
            # Encontrar el día del máximo y mínimo
            for i, candle in enumerate(candles):
                if candle.high == max_price:
                    high_days.append(i + 1)  # +1 porque el primer día es día 1
                if candle.low == min_price:
                    low_days.append(i + 1)
        
        # Distribución por días
        max_days = max(high_days + low_days) if (high_days or low_days) else 1
        day_high_dist = {}
        day_low_dist = {}
        
        for d in range(1, max_days + 1):
            day_high_dist[str(d)] = high_days.count(d)
            day_low_dist[str(d)] = low_days.count(d)
            
        return {
            'most_common_high_day': max(day_high_dist.items(), key=lambda x: x[1])[0] if high_days else None,
            'most_common_low_day': max(day_low_dist.items(), key=lambda x: x[1])[0] if low_days else None,
            'daily_high_distribution': day_high_dist,
            'daily_low_distribution': day_low_dist
        }
    
    def _calculate_performance_stats(self) -> dict[str, Any]:
        """Estadísticas de rendimiento detalladas"""
        if not self.candles_data:
            return {}
            
        all_returns = []
        max_favorable = []
        max_adverse = []
        
        for symbol_data in self.candles_data.values():
            candles = symbol_data['candles']
            entry_price = symbol_data['entry_price']
            
            if not candles:
                continue
                
            prices = [c.close for c in candles]
            highs = [c.high for c in candles]
            lows = [c.low for c in candles]
            
            # Retorno final
            final_return = (prices[-1] - entry_price) / entry_price * 100
            all_returns.append(final_return)
            
            # Máximo movimiento favorable y adverso
            max_high = max(highs)
            min_low = min(lows)
            
            max_fav = (max_high - entry_price) / entry_price * 100
            max_adv = (min_low - entry_price) / entry_price * 100
            
            max_favorable.append(max_fav)
            max_adverse.append(max_adv)
        
        if not all_returns:
            return {}
            
        return {
            'avg_max_favorable': np.mean(max_favorable),
            'avg_max_adverse': np.mean(max_adverse),
            'sharpe_ratio': np.mean(all_returns) / np.std(all_returns) if np.std(all_returns) > 0 else 0,
            'profit_factor': abs(np.mean([r for r in all_returns if r > 0])) / abs(np.mean([r for r in all_returns if r < 0])) if any(r < 0 for r in all_returns) else float('inf'),
            'max_drawdown': np.min(max_adverse)
        }
    
    def _calculate_volatility_stats(self) -> dict[str, Any]:
        """Análisis de volatilidad"""
        if not self.candles_data:
            return {}
            
        daily_ranges = []
        
        for symbol_data in self.candles_data.values():
            candles = symbol_data['candles']
            
            for candle in candles:
                daily_range = (candle.high - candle.low) / candle.open * 100
                daily_ranges.append(daily_range)
        
        if not daily_ranges:
            return {}
            
        return {
            'avg_daily_range': np.mean(daily_ranges),
            'median_daily_range': np.median(daily_ranges),
            'volatility': np.std(daily_ranges)
        }
    
    def _analyze_breakouts(self) -> dict[str, Any]:
        """Análisis de rupturas de máximos/mínimos"""
        if not self.candles_data:
            return {}
            
        breakout_stats = {
            'high_breaks': 0,
            'low_breaks': 0,
            'total_opportunities': 0
        }
        
        for symbol_data in self.candles_data.values():
            candles = symbol_data['candles']
            
            if len(candles) < 2:
                continue
                
            for i in range(1, len(candles)):
                prev_high = max(c.high for c in candles[:i])
                prev_low = min(c.low for c in candles[:i])
                
                current = candles[i]
                
                breakout_stats['total_opportunities'] += 1
                
                if current.high > prev_high:
                    breakout_stats['high_breaks'] += 1
                if current.low < prev_low:
                    breakout_stats['low_breaks'] += 1
        
        total_ops = breakout_stats['total_opportunities']
        if total_ops > 0:
            breakout_stats['high_break_rate'] = breakout_stats['high_breaks'] / total_ops * 100
            breakout_stats['low_break_rate'] = breakout_stats['low_breaks'] / total_ops * 100
        
        return breakout_stats
    
    def _prepare_chart_data(self, is_daytrading: bool) -> dict[str, Any]:
        """Preparar datos para los gráficos"""
        if not self.candles_data:
            return {}
            
        # Datos para gráfico de Monte Carlo
        monte_carlo_data = []
        heatmap_data = []
        
        # Normalizar todas las series a partir del precio de entrada (100%)
        max_length = 0
        
        for symbol_data in self.candles_data.values():
            candles = symbol_data['candles']
            entry_price = symbol_data['entry_price']
            
            if not candles:
                continue
                
            normalized_prices = []
            for i, candle in enumerate(candles):
                normalized_price = (candle.close / entry_price) * 100
                
                if is_daytrading:
                    time_point = i * (1/60)  # Minutos a horas
                else:
                    time_point = i  # Días
                    
                normalized_prices.append({
                    'x': time_point,
                    'y': normalized_price,
                    'symbol': symbol_data['entry'].symbol
                })
            
            monte_carlo_data.append(normalized_prices)
            max_length = max(max_length, len(normalized_prices))
        
        # Calcular percentiles y media para cada punto temporal
        percentile_data = {'mean': [], 'p25': [], 'p75': [], 'p10': [], 'p90': []}
        
        for t in range(max_length):
            values_at_t = []
            for series in monte_carlo_data:
                if t < len(series):
                    values_at_t.append(series[t]['y'])
            
            if values_at_t:
                time_val = t * (1/60 if is_daytrading else 1)
                percentile_data['mean'].append({'x': time_val, 'y': np.mean(values_at_t)})
                percentile_data['p25'].append({'x': time_val, 'y': np.percentile(values_at_t, 25)})
                percentile_data['p75'].append({'x': time_val, 'y': np.percentile(values_at_t, 75)})
                percentile_data['p10'].append({'x': time_val, 'y': np.percentile(values_at_t, 10)})
                percentile_data['p90'].append({'x': time_val, 'y': np.percentile(values_at_t, 90)})
        
        # Datos para heatmap (probabilidad de máximos/mínimos)
        heatmap_data = self._generate_heatmap_data(is_daytrading)
        
        return {
            'monte_carlo_traces': monte_carlo_data,
            'percentile_data': percentile_data,
            'heatmap_data': heatmap_data
        }
    
    def _generate_heatmap_data(self, is_daytrading: bool) -> list[dict]:
        """Generar datos para el heatmap de probabilidades"""
        if not self.candles_data:
            return []
            
        # Grid para el heatmap
        time_bins = 24 if is_daytrading else 10  # 24 horas o 10 días máximo
        price_bins = 20  # 20 niveles de precio
        
        # Matriz para contar extremos
        high_matrix = np.zeros((price_bins, time_bins))
        low_matrix = np.zeros((price_bins, time_bins))
        total_matrix = np.zeros((price_bins, time_bins))
        
        for symbol_data in self.candles_data.values():
            candles = symbol_data['candles']
            entry_price = symbol_data['entry_price']
            
            if not candles:
                continue
                
            # Normalizar precios (80% - 120% del precio de entrada)
            price_range = (0.8, 1.2)
            
            for i, candle in enumerate(candles):
                if is_daytrading:
                    time_idx = min(candle.date.hour, time_bins - 1)
                else:
                    time_idx = min(i, time_bins - 1)
                
                # Normalizar precio
                norm_high = candle.high / entry_price
                norm_low = candle.low / entry_price
                
                # Convertir a índices de precio
                high_price_idx = int((norm_high - price_range[0]) / (price_range[1] - price_range[0]) * (price_bins - 1))
                low_price_idx = int((norm_low - price_range[0]) / (price_range[1] - price_range[0]) * (price_bins - 1))
                
                # Asegurar que están en rango
                high_price_idx = max(0, min(price_bins - 1, high_price_idx))
                low_price_idx = max(0, min(price_bins - 1, low_price_idx))
                
                # Marcar como extremos si son máximos/mínimos del día o período
                is_period_high = candle.high == max(c.high for c in candles[max(0, i-5):i+6])  # Ventana de 11 períodos
                is_period_low = candle.low == min(c.low for c in candles[max(0, i-5):i+6])
                
                if is_period_high:
                    high_matrix[high_price_idx, time_idx] += 1
                if is_period_low:
                    low_matrix[low_price_idx, time_idx] += 1
                    
                total_matrix[high_price_idx, time_idx] += 1
                if high_price_idx != low_price_idx:
                    total_matrix[low_price_idx, time_idx] += 1
        
        # Convertir a probabilidades y formato para el gráfico
        heatmap_data = []
        for price_idx in range(price_bins):
            for time_idx in range(time_bins):
                if total_matrix[price_idx, time_idx] > 0:
                    high_prob = high_matrix[price_idx, time_idx] / total_matrix[price_idx, time_idx]
                    low_prob = low_matrix[price_idx, time_idx] / total_matrix[price_idx, time_idx]
                    
                    # Combinar probabilidades (verde para máximos, rojo para mínimos)
                    combined_prob = high_prob - low_prob  # Rango de -1 a 1
                    
                    price_level = price_range[0] + (price_idx / (price_bins - 1)) * (price_range[1] - price_range[0])
                    
                    heatmap_data.append({
                        'x': time_idx,
                        'y': price_level * 100,  # Convertir a porcentaje
                        'z': combined_prob
                    })
        
        return heatmap_data
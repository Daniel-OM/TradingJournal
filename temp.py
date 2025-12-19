
from datetime import datetime, timedelta

import numpy as np

from journal.src.yahoofinance import YahooTicker

yf = YahooTicker('AAPL')

timeframe = '1d'
end = datetime.now()
if timeframe == '1d':
    start = end - timedelta(days=365*10)
else:
    start = end - timedelta(days=7)

price = yf.getPrice(start=start, end=end, timeframe=timeframe, df=True)
price['bullish'] = np.where(price['close'] > price['open'], 1, 
                    np.where(price['close'] < price['open'], -1, 0))

prob_bull = price[price['bullish'] > 0].size / price.size
prob_bear = price[price['bullish'] < 0].size / price.size
prob_scratch = price[price['bullish'] == 0].size / price.size

print('Bullish prob: ', prob_bull, 
      '\nBearish prob: ', prob_bear, 
      '\nScratch prob: ', prob_scratch)

price['continuity'] = np.where((price['close'].shift(1) > price['open'].shift(1)) & (price['close'] > price['open']), '11', 
                        np.where((price['close'].shift(1) > price['open'].shift(1)) & (price['close'] < price['open']), '1-1', 
                        np.where((price['close'].shift(1) > price['open'].shift(1)) & (price['close'] == price['open']), '10', 
                    np.where((price['close'].shift(1) < price['open'].shift(1)) & (price['close'] > price['open']), '-11', 
                        np.where((price['close'].shift(1) < price['open'].shift(1)) & (price['close'] < price['open']), '-1-1', 
                        np.where((price['close'].shift(1) < price['open'].shift(1)) & (price['close'] == price['open']), '-10',
                    np.where((price['close'].shift(1) == price['open'].shift(1)) & (price['close'] > price['open']), '01', 
                        np.where((price['close'].shift(1) == price['open'].shift(1)) & (price['close'] < price['open']), '0-1', 
                        np.where((price['close'].shift(1) == price['open'].shift(1)) & (price['close'] == price['open']), '00',  
                    '')))))))))

print('Bullish-Bullish prob: ', price[price['continuity'] == '11'].size / price.size, 
      '\nBullish-Bearish prob: ', price[price['continuity'] == '1-1'].size / price.size,  
      '\nBullish-Scratch prob: ', price[price['continuity'] == '10'].size / price.size, 
      '\nBearish-Bullish prob: ', price[price['continuity'] == '-11'].size / price.size, 
      '\nBearish-Bearish prob: ', price[price['continuity'] == '-1-1'].size / price.size,  
      '\nBearish-Scratch prob: ', price[price['continuity'] == '-10'].size / price.size, 
      '\nScratch-Bullish prob: ', price[price['continuity'] == '01'].size / price.size, 
      '\nScratch-Bearish prob: ', price[price['continuity'] == '0-1'].size / price.size,  
      '\nScratch-Scratch prob: ', price[price['continuity'] == '00'].size / price.size, )

print('Trending prob: ', price[(price['continuity'] == '11')
                               | (price['continuity'] == '10')
                               | (price['continuity'] == '-1-1')
                               | (price['continuity'] == '-10')
                               | (price['continuity'] == '01')
                               | (price['continuity'] == '0-1')].size / price.size,
        '\nReverting prob: ', price[(price['continuity'] == '1-1')
                               | (price['continuity'] == '-11')
                               | (price['continuity'] == '00')].size / price.size)

def probCalc(df, bull:int):

    if df.size > 0:
        cond = (df['bullish'].shift(1) > 0) if bull > 0 else ((df['bullish'].shift(1) < 0) if bull < 0 else (df['bullish'].shift(1) == 0))
        pbull = df[cond & (df['close'] > df['open'])].size / df.size
        pbear = df[cond & (df['close'] < df['open'])].size / df.size
        pscratch = df[cond & (df['close'] == df['open'])].size / df.size
    else:
        pbull = 0
        pbear = 0
        pscratch = 0

    return pbull, pbear, pscratch

for i, idx in enumerate(price.index):
    candle = price.loc[idx]
    if candle['bullish'] > 0:
        prob = {
            '10': price.iloc[i-10:i],
            '20': price.iloc[i-20:i],
            '50': price.iloc[i-50:i],
            '100': price.iloc[i-100:i],
            '200': price.iloc[i-200:i]
        }
        prob = {k: probCalc(v, 1) for k, v in prob.items()}














"""
Script: Minimal HMM-based prediction (without hmmlearn or sklearn)
Language: Python 3.10+

Descripción:
- Implementación básica de un HMM con emisiones gaussianas usando solo numpy/pandas.
- Entrena dos modelos separados para dirección y volatilidad.
- Combina predicciones de varias ventanas temporales.

Dependencias:
- numpy, pandas

"""

from __future__ import annotations
import numpy as np
import pandas as pd
from typing import List, Dict

# ------------------------- Utilidades -------------------------

def compute_returns(df: pd.DataFrame) -> pd.Series:
    return np.log(df['close']).diff().fillna(0)

def rolling_volatility(returns: pd.Series, window: int) -> pd.Series:
    return returns.rolling(window).std().fillna(method='bfill')

# ------------------------- HMM mínimo -------------------------
class GaussianHMMMinimal:
    def __init__(self, n_states: int = 2, n_iter: int = 20, random_state: int = 42):
        self.n_states = n_states
        self.n_iter = n_iter
        self.rng = np.random.default_rng(random_state)

    def _gaussian_prob(self, x, mean, var):
        return (1.0 / np.sqrt(2 * np.pi * var)) * np.exp(-0.5 * ((x - mean) ** 2) / var)

    def fit(self, X: np.ndarray):
        # X: shape (n_samples,)
        n = len(X)
        # inicializar parámetros
        self.pi = np.ones(self.n_states) / self.n_states
        self.A = np.ones((self.n_states, self.n_states)) / self.n_states
        self.means = self.rng.normal(np.mean(X), np.std(X), self.n_states)
        self.vars = np.ones(self.n_states) * np.var(X)

        for _ in range(self.n_iter):
            # forward
            alpha = np.zeros((n, self.n_states))
            for s in range(self.n_states):
                alpha[0, s] = self.pi[s] * self._gaussian_prob(X[0], self.means[s], self.vars[s])
            alpha[0, :] /= np.sum(alpha[0, :])
            for t in range(1, n):
                for s in range(self.n_states):
                    prob = self._gaussian_prob(X[t], self.means[s], self.vars[s])
                    alpha[t, s] = prob * np.sum(alpha[t - 1, :] * self.A[:, s])
                alpha[t, :] /= np.sum(alpha[t, :])

            # backward
            beta = np.zeros((n, self.n_states))
            beta[-1, :] = 1.0
            for t in reversed(range(n - 1)):
                for s in range(self.n_states):
                    beta[t, s] = np.sum(beta[t + 1, :] * self.A[s, :] * [self._gaussian_prob(X[t + 1], self.means[j], self.vars[j]) for j in range(self.n_states)])
                beta[t, :] /= np.sum(beta[t, :])

            # gamma y xi
            gamma = (alpha * beta)
            gamma /= gamma.sum(axis=1, keepdims=True)

            xi = np.zeros((n - 1, self.n_states, self.n_states))
            for t in range(n - 1):
                denom = np.sum(alpha[t, :] * beta[t, :])
                for i in range(self.n_states):
                    for j in range(self.n_states):
                        xi[t, i, j] = alpha[t, i] * self.A[i, j] * self._gaussian_prob(X[t + 1], self.means[j], self.vars[j]) * beta[t + 1, j]
                xi[t, :, :] /= np.sum(xi[t, :, :])

            # reestimación parámetros
            self.pi = gamma[0]
            self.A = xi.sum(axis=0)
            self.A /= self.A.sum(axis=1, keepdims=True)
            for s in range(self.n_states):
                weight = gamma[:, s]
                self.means[s] = np.sum(weight * X) / np.sum(weight)
                self.vars[s] = np.sum(weight * (X - self.means[s]) ** 2) / np.sum(weight)

        self.last_gamma = gamma

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        n = len(X)
        alpha = np.zeros((n, self.n_states))
        for s in range(self.n_states):
            alpha[0, s] = self.pi[s] * self._gaussian_prob(X[0], self.means[s], self.vars[s])
        alpha[0, :] /= np.sum(alpha[0, :])
        for t in range(1, n):
            for s in range(self.n_states):
                prob = self._gaussian_prob(X[t], self.means[s], self.vars[s])
                alpha[t, s] = prob * np.sum(alpha[t - 1, :] * self.A[:, s])
            alpha[t, :] /= np.sum(alpha[t, :])
        return alpha

# ------------------------- Ensamble sencillo -------------------------
class HMMEnsembleMinimal:
    def __init__(self, window_sizes: List[int], n_states: int = 2):
        self.window_sizes = window_sizes
        self.n_states = n_states
        self.models: Dict[int, GaussianHMMMinimal] = {}

    def fit(self, df: pd.DataFrame):
        returns = compute_returns(df)
        for w in self.window_sizes:
            X = returns.rolling(w).mean().dropna().values
            model = GaussianHMMMinimal(n_states=self.n_states)
            model.fit(X)
            self.models[w] = model

    def predict_one(self, df: pd.DataFrame) -> Dict[str, float]:
        returns = compute_returns(df)
        preds = []
        for w in self.window_sizes:
            if len(returns) < w:
                continue
            X = returns[-w:].values
            model = self.models[w]
            post = model.predict_proba(X)[-1]
            p_up = post.mean()  # aproximación muy simple
            preds.append(p_up)
        if not preds:
            raise ValueError("No hay suficientes datos.")
        p_up_final = float(np.mean(preds))
        return {"p_up": p_up_final, "pred_class": int(p_up_final > 0.5)}

# ------------------------- Ejemplo -------------------------
if __name__ == "__main__":

    model = HMMEnsembleMinimal(window_sizes=[5, 10], n_states=2)
    model.fit(price)
    pred = model.predict_one(price)
    print("Predicción:", pred)



"""
Script: Predictores heurísticos de dirección y volatilidad (sin HMM, sin entrenamiento iterativo)
Language: Python 3.10+

Descripción:
- Implementación no académica y determinista que sigue tu idea: no hay EM ni forward-backward.
- Se construyen DOS modelos independientes (dirección y volatilidad), ambos con 3 estados:
  - Dirección: UP, SIDE, DOWN. El umbral para considerar "UP" o "DOWN" se basa en las comisiones (en % o absoluta).
  - Volatilidad: LOW, MID, HIGH. Se definen según cuantiles históricos de volatilidad.
- Para cada ventana temporal (listas de ventanas configurables) se calcula:
  - Secuencia de estados históricos.
  - Matriz de transición empírica P(next_state | prev_state).
  - Estadísticas por estado de la variable de interés (probabilidad de subida, volatilidad esperada, retorno medio).
- Predicción:
  1) Se obtiene el estado actual (último) según cada ventana.
  2) Para cada ventana se extrae la fila correspondiente de la matriz de transición → distribución de estados futuros.
  3) Se traduce esa distribución en probabilidad de subida y volatilidad esperada usando las estadísticas por estado.
  4) Se combinan las predicciones de todas las ventanas con pesos basados en la precisión en un bloque de validación (por defecto el último 20% de cada serie).

Ventajas de este enfoque:
- Determinista, rápido, interpretable.
- Fácil de integrar en sistemas de ejecución en tiempo real.
- Los estados son explícitos y fáciles de explicar.

Limitaciones:
- Depende de las etiquetas heurísticas (umbral de comisión y de volatilidad). Si cambias la definición de "subida relevante" cambian todas las estadísticas.
- No captura patrones complejos que un HMM entrenado podría descubrir automáticamente.

Uso:
- Llama a `DirectionVolModel(...).fit(df)` y `VolatilityModel(...).fit(df)` o usa la clase combinada `EnsembleHeuristic`.
- Para predecir un día se usa `predict_one(df)` con el DataFrame hasta la fecha actual.

"""

from __future__ import annotations
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional

# ------------------------- Utilidades -------------------------

def compute_returns(df: pd.DataFrame) -> pd.Series:
    """Retornos simples (pct change) alineados con índice de precios."""
    return df['close'].pct_change().fillna(0)

# ------------------------- Etiquetado de estados (dirección) -------------------------

def label_direction(next_returns: np.ndarray, thr_up: float, thr_down: float) -> np.ndarray:
    """Devuelve etiquetas: 0=DOWN, 1=SIDE, 2=UP"""
    labels = np.ones(len(next_returns), dtype=int)  # default SIDE
    labels[next_returns > thr_up] = 2
    labels[next_returns < thr_down] = 0
    return labels


# ------------------------- Modelo heurístico por ventanas -------------------------
class HeuristicModel:
    """Clase base con utilidades comunes."""
    def __init__(self, window_sizes: List[int], val_frac: float = 0.2):
        self.window_sizes = sorted(window_sizes)
        self.val_frac = val_frac
        # por ventana guardamos: transition matrix, stats por estado, val_acc, n_obs
        self.models: Dict[int, Dict] = {}

    @staticmethod
    def _transition_matrix(prev_states: np.ndarray, next_states: np.ndarray, n_states: int) -> np.ndarray:
        """Calcula matriz de transición empírica P(next | prev)."""
        T = np.zeros((n_states, n_states), dtype=float)
        for a, b in zip(prev_states, next_states):
            T[a, b] += 1
        # normalizar filas (si fila suma 0 -> repartir uniformemente)
        row_sums = T.sum(axis=1, keepdims=True)
        zero_rows = (row_sums.squeeze() == 0)
        T[~zero_rows] /= row_sums[~zero_rows]
        if np.any(zero_rows):
            T[zero_rows, :] = 1.0 / n_states
        return T

# ------------------------- Modelo de dirección (3 estados) -------------------------
class DirectionModel(HeuristicModel):
    """Modelo no iterativo que etiqueta 3 estados: DOWN(0), SIDE(1), UP(2).
    - threshold puede ser un % (por defecto) o un umbral absoluto por precio (pasando commission_abs).
    """
    def __init__(self, window_sizes: List[int], commission_pct: Optional[float] = 0.001, commission_abs: Optional[float] = None, val_frac: float = 0.2):
        super().__init__(window_sizes, val_frac)
        self.commission_pct = commission_pct
        self.commission_abs = commission_abs
        self.n_states = 3

    def _return_threshold(self, last_price: float) -> Tuple[float, float]:
        """Devuelve umbral positivo y negativo en términos de retorno porcentual.
        Si commission_abs está dado, lo convierte en porcentaje respecto a last_price.
        """
        if self.commission_abs is not None:
            thr = self.commission_abs / last_price
        else:
            thr = self.commission_pct if self.commission_pct is not None else 0.0
        return thr, -thr

    def fit(self, df: pd.DataFrame):
        returns = compute_returns(df).values
        prices = df['close'].values
        n = len(returns)
        for w in self.window_sizes:
            # build samples: for t from w-1 .. n-2 we can use prev_window ending at t and next return at t+1
            prev_states = []
            next_states = []
            next_returns = []
            for end in range(w - 1, n - 1):
                # compute prev window features if needed (we only need to compute last return of window to classify 'prev state')
                # but we follow your idea: prev state is classification of the return that closed the window (or could be aggregate)
                prev_return = returns[end]
                # threshold based on price at end
                thr_up, thr_down = self._return_threshold(prices[end])
                # label prev and next
                prev_label = 2 if prev_return > thr_up else (0 if prev_return < thr_down else 1)
                nr = returns[end + 1]
                next_label = 2 if nr > thr_up else (0 if nr < thr_down else 1)

                prev_states.append(prev_label)
                next_states.append(next_label)
                next_returns.append(nr)

            prev_states = np.array(prev_states, dtype=int)
            next_states = np.array(next_states, dtype=int)
            next_returns = np.array(next_returns, dtype=float)

            # split temporal: train = first (1-val_frac), val = last val_frac
            split = int(len(prev_states) * (1 - self.val_frac))
            if split < 1:
                split = 1
            train_prev, val_prev = prev_states[:split], prev_states[split:]
            train_next, val_next = next_states[:split], next_states[split:]
            train_next_returns, val_next_returns = next_returns[:split], next_returns[split:]

            T = self._transition_matrix(train_prev, train_next, self.n_states)

            # stats por estado (calculadas en train): prob de subida en next, prob de bajada, vol esperada (abs next return), retorno medio
            stats = {}
            for s in range(self.n_states):
                mask = (train_prev == s)
                if np.any(mask):
                    nxt = train_next[mask]
                    nxt_ret = train_next_returns[mask]
                    p_up = np.mean(nxt == 2)
                    p_down = np.mean(nxt == 0)
                    exp_vol = np.mean(np.abs(nxt_ret))
                    mean_ret = np.mean(nxt_ret)
                    stats[s] = {'p_up': float(p_up), 'p_down': float(p_down), 'exp_vol': float(exp_vol), 'mean_ret': float(mean_ret), 'n': int(mask.sum())}
                else:
                    stats[s] = {'p_up': 1/3, 'p_down':1/3, 'exp_vol': float(np.mean(np.abs(train_next_returns))), 'mean_ret':0.0, 'n':0}

            # validar: predecir next state usando T[val_prev_row].argmax and comparar con val_next
            if len(val_prev) > 0:
                preds = [T[row].argmax() for row in val_prev]
                val_acc = float((np.array(preds) == val_next).mean())
            else:
                val_acc = 0.5

            self.models[w] = {'T': T, 'stats': stats, 'val_acc': val_acc, 'n_obs': len(train_prev)}

    def predict_one(self, df: pd.DataFrame) -> Dict:
        returns = compute_returns(df).values
        prices = df['close'].values
        n = len(returns)
        window_results = []
        for w in self.window_sizes:
            if n < w:
                continue
            last_idx = n - 1
            prev_return = returns[last_idx]
            thr_up, thr_down = self._return_threshold(prices[last_idx])
            prev_state = 2 if prev_return > thr_up else (0 if prev_return < thr_down else 1)

            m = self.models[w]
            T = m['T']
            dist_next = T[prev_state]  # distribución P(next_state | prev_state)
            # convertir a prob de subida y vol esperada
            stats = m['stats']
            p_up = sum(dist_next[s] * stats[s]['p_up'] for s in range(self.n_states))
            exp_vol = sum(dist_next[s] * stats[s]['exp_vol'] for s in range(self.n_states))
            window_results.append({'window': w, 'weight': m['val_acc'], 'p_up': p_up, 'exp_vol': exp_vol, 'dist_next': dist_next.copy(), 'prev_state': int(prev_state)})

        if not window_results:
            raise ValueError('No hay suficientes datos para ninguna ventana.')

        # combinar con pesos proporcionales a val_acc (suavizado)
        weights = np.array([wr['weight']/(wr['window']**2) for wr in window_results], dtype=float)
        weights /= weights.sum()
        print(weights)

        p_up_agg = float(sum(wr['p_up'] * wt for wr, wt in zip(window_results, weights)))
        vol_agg = float(sum(wr['exp_vol'] * wt for wr, wt in zip(window_results, weights)))
        agg_dist = sum(wt * wr['dist_next'] for wr, wt in zip(window_results, weights))
        pred_class = int(p_up_agg > 0.5)
        pred_state = int(np.argmax(agg_dist))

        return {'p_up': p_up_agg, 'pred_state': pred_state, 'exp_vol': vol_agg, 'details': window_results}

# ------------------------- Modelo de volatilidad (3 estados) -------------------------
class VolatilityModel(HeuristicModel):
    """Modela volatilidad histórica en 3 estados: LOW(0), MID(1), HIGH(2)."""
    def __init__(self, window_sizes: List[int], vol_window_for_label: int = 20, val_frac: float = 0.2):
        super().__init__(window_sizes, val_frac)
        self.n_states = 3
        self.vol_window_for_label = vol_window_for_label
        
    def rolling_volatility(self, returns: pd.Series, window: int) -> pd.Series:
        """Volatilidad histórica: std de retornos en ventana móvil (usamos ddof=0)."""
        return returns.rolling(window).std().fillna(method='bfill')
    
    def label_volatility(self, vol_series: np.ndarray) -> np.ndarray:
        """Etiqueta vol en 0=LOW,1=MID,2=HIGH usando terciles históricos."""
        q1 = np.nanquantile(vol_series, 1/3)
        q2 = np.nanquantile(vol_series, 2/3)
        labels = np.zeros(len(vol_series), dtype=int)
        labels[vol_series > q1] = 1
        labels[vol_series > q2] = 2
        return labels

    def fit(self, df: pd.DataFrame):
        returns = compute_returns(df)
        vol_series = self.rolling_volatility(returns, self.vol_window_for_label).values
        n = len(vol_series)
        vol_labels = self.label_volatility(vol_series)

        for w in self.window_sizes:
            prev_states = []
            next_states = []
            next_vol = []
            for end in range(w - 1, n - 1):
                prev_states.append(vol_labels[end])
                next_states.append(vol_labels[end + 1])
                next_vol.append(vol_series[end + 1])

            prev_states = np.array(prev_states, dtype=int)
            next_states = np.array(next_states, dtype=int)
            next_vol = np.array(next_vol, dtype=float)

            split = int(len(prev_states) * (1 - self.val_frac))
            if split < 1:
                split = 1
            train_prev, val_prev = prev_states[:split], prev_states[split:]
            train_next, val_next = next_states[:split], next_states[split:]
            train_next_vol, val_next_vol = next_vol[:split], next_vol[split:]

            T = self._transition_matrix(train_prev, train_next, self.n_states)

            stats = {}
            for s in range(self.n_states):
                mask = (train_prev == s)
                if np.any(mask):
                    nxt = train_next[mask]
                    nxt_vol = train_next_vol[mask]
                    exp_vol = float(np.mean(nxt_vol))
                    stats[s] = {'exp_vol': exp_vol, 'n': int(mask.sum())}
                else:
                    stats[s] = {'exp_vol': float(np.mean(train_next_vol)), 'n': 0}

            if len(val_prev) > 0:
                preds = [T[row].argmax() for row in val_prev]
                val_acc = float((np.array(preds) == val_next).mean())
            else:
                val_acc = 0.5

            self.models[w] = {'T': T, 'stats': stats, 'val_acc': val_acc, 'n_obs': len(train_prev)}

    def predict_one(self, df: pd.DataFrame) -> Dict:
        returns = compute_returns(df)
        vol_series = self.rolling_volatility(returns, self.vol_window_for_label).values
        n = len(vol_series)
        vol_labels = self.label_volatility(vol_series)

        window_results = []
        for w in self.window_sizes:
            if n < w:
                continue
            last_idx = n - 1
            prev_state = int(vol_labels[last_idx])
            m = self.models[w]
            T = m['T']
            dist_next = T[prev_state]
            stats = m['stats']
            exp_vol = sum(dist_next[s] * stats[s]['exp_vol'] for s in range(self.n_states))
            window_results.append({'window': w, 'weight': m['val_acc'], 'exp_vol': exp_vol, 'dist_next': dist_next.copy().tolist(), 'prev_state': prev_state})

        if not window_results:
            raise ValueError('No hay suficientes datos para ninguna ventana.')

        weights = np.array([wr['weight']/(wr['window']**2) for wr in window_results], dtype=float)
        weights /= weights.sum()

        vol_agg = float(sum(wr['exp_vol'] * wt for wr, wt in zip(window_results, weights)))
        return {'exp_vol': vol_agg, 'details': window_results}

# ------------------------- Clase combinada (opcional) -------------------------
class EnsembleHeuristic:
    def __init__(self, dir_windows: List[int], vol_windows: List[int], commission_pct: Optional[float] = 0.001, commission_abs: Optional[float] = None, vol_window_for_label: int = 20, val_frac: float = 0.2):
        self.dir_model = DirectionModel(dir_windows, commission_pct=commission_pct, commission_abs=commission_abs, val_frac=val_frac)
        self.vol_model = VolatilityModel(vol_windows, vol_window_for_label=vol_window_for_label, val_frac=val_frac)

    def fit(self, df: pd.DataFrame):
        self.dir_model.fit(df)
        self.vol_model.fit(df)

    def predict_one(self, df: pd.DataFrame) -> Dict:
        d = self.dir_model.predict_one(df)
        v = self.vol_model.predict_one(df)
        # combinar detalles
        res = {'p_up': d['p_up'], 'pred_state': d['pred_state'], 'exp_vol': v['exp_vol'], 'dir_details': d['details'], 'vol_details': v['details']}
        return res

# ------------------------- Ejemplo de uso -------------------------
if __name__ == '__main__':

    ensemble = EnsembleHeuristic(dir_windows=[5, 10, 20, 50, 100, 200], vol_windows=[10, 20, 50], commission_pct=0.001, vol_window_for_label=20)
    ensemble.fit(price)
    pred = ensemble.predict_one(price)

    print('Probabilidad agregada de subida:', round(pred['p_up'], 4))
    print('Clase predicha (0=baja, 1=lateral, 2=subida):', pred['pred_state'])
    print('Volatilidad esperada (std de retornos):', round(pred['exp_vol'], 6))
    print('\nDetalles (dirección):')
    for d in pred['dir_details']:
        print(f"ventana={d['window']}, peso(val_acc)={d['weight']:.3f}, p_up={d['p_up']:.3f}, prev_state={d['prev_state']}, dist_next={d['dist_next']}")
    print('\nDetalles (volatilidad):')
    for v in pred['vol_details']:
        print(f"ventana={v['window']}, peso(val_acc)={v['weight']:.3f}, exp_vol={v['exp_vol']:.5f}, prev_state={v['prev_state']}, dist_next={v['dist_next']}")

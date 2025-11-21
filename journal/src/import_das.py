
from __future__ import annotations
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, date, timedelta, timezone
from typing import Optional
from dataclasses import dataclass, field
from enum import Enum


class TradeSide(Enum):
    """Enum para lados de trading"""
    LONG = 1
    SHORT = -1
    
    @classmethod
    def from_string(cls, value: str) -> TradeSide:
        """Parsea string a TradeSide"""
        v = str(value).strip().upper()
        if v in ('B', 'BUY', 'LONG'):
            return cls.LONG
        elif v in ('S', 'SELL', 'SHORT'):
            return cls.SHORT
        return cls.LONG  # default


@dataclass
class Execution:
    """Representa una ejecución individual"""
    datetime: datetime
    price: float
    quantity: float
    side: TradeSide
    raw_data: pd.Series
    
    @property
    def signed_quantity(self) -> float:
        """Cantidad con signo según el lado"""
        return self.quantity * self.side.value
    
    @property
    def notional(self) -> float:
        """Valor nocional de la ejecución"""
        return self.price * self.quantity
    
    @classmethod
    def from_row(cls, row: pd.Series, 
                 time_col: str = 'time',
                 price_col: str = 'price',
                 qty_col: str = 'qty',
                 side_col: str = 'B/S') -> Execution:
        """Factory method para crear Execution desde pandas Series"""
        dt: datetime = cls._parse_datetime(row=row, time_col=time_col)
        side: TradeSide = TradeSide.from_string(value=row[side_col])
        
        return cls(
            datetime=dt,
            price=float(row[price_col]),
            quantity=float(row[qty_col]),
            side=side,
            raw_data=row
        )
    
    @staticmethod
    def _parse_datetime(row: pd.Series, time_col: str) -> datetime:
        """Parsea datetime desde row"""
        time_str: str = str(row[time_col]).strip()
        try:
            dt: datetime = datetime.strptime(time_str, '%m/%d/%y %H:%M:%S')
            return dt.replace(tzinfo=timezone.utc)
        except ValueError as e:
            raise ValueError(f"Error parseando tiempo '{time_str}': {e}")
    
    def split(self, qty_to_take: float) -> tuple[Execution, Optional[Execution]]:
        """
        Divide la ejecución en dos partes.
        Returns: (ejecución con qty_to_take, ejecución con resto o None)
        """
        if qty_to_take >= self.quantity:
            return self, None
        
        remaining_qty: float = self.quantity - qty_to_take
        
        first = Execution(
            datetime=self.datetime,
            price=self.price,
            quantity=qty_to_take,
            side=self.side,
            raw_data=self.raw_data.copy()
        )
        
        second = Execution(
            datetime=self.datetime,
            price=self.price,
            quantity=remaining_qty,
            side=self.side,
            raw_data=self.raw_data.copy()
        )
        
        return first, second


@dataclass
class Trade:
    """Representa un trade completo con sus ejecuciones"""
    symbol: str
    executions: list[Execution] = field(default_factory=list)
    _position: float = 0.0
    
    @property
    def is_closed(self) -> bool:
        """Verifica si el trade está cerrado"""
        return abs(self._position) < 1e-9
    
    @property
    def trade_type(self) -> TradeSide:
        """Tipo de trade basado en primera ejecución"""
        return self.executions[0].side if self.executions else TradeSide.LONG
    
    @property
    def entries(self) -> list[Execution]:
        """Ejecuciones de entrada"""
        return [e for e in self.executions if e.side == self.trade_type]
    
    @property
    def exits(self) -> list[Execution]:
        """Ejecuciones de salida"""
        return [e for e in self.executions if e.side != self.trade_type]
    
    def add_execution(self, execution: Execution) -> None:
        """Añade ejecución al trade"""
        self.executions.append(execution)
        self._position += execution.signed_quantity
    
    def vwap(self, executions: list[Execution]) -> Optional[float]:
        """Calcula VWAP de una lista de ejecuciones"""
        if not executions:
            return None
        
        total_notional = sum(e.notional for e in executions)
        total_qty = sum(e.quantity for e in executions)
        
        return total_notional / total_qty if total_qty > 0 else None
    
    @property
    def entry_vwap(self) -> Optional[float]:
        """VWAP de entradas"""
        return self.vwap(executions=self.entries)
    
    @property
    def exit_vwap(self) -> Optional[float]:
        """VWAP de salidas"""
        return self.vwap(executions=self.exits)
    
    @property
    def entry_quantity(self) -> float:
        """Cantidad total de entrada"""
        return sum(e.quantity for e in self.entries)
    
    @property
    def exit_quantity(self) -> float:
        """Cantidad total de salida"""
        return sum(e.quantity for e in self.exits)
    
    @property
    def gross_pnl(self) -> Optional[float]:
        """P&L bruto sin comisiones"""
        if not self.entry_vwap or not self.exit_vwap or self.exit_quantity == 0:
            return None
        
        multiplier = self.trade_type.value
        return (self.exit_vwap - self.entry_vwap) * multiplier * self.exit_quantity
    
    @property
    def start_datetime(self) -> datetime:
        """Datetime de inicio"""
        return self.executions[0].datetime if self.executions else None
    
    @property
    def end_datetime(self) -> datetime:
        """Datetime de fin"""
        return self.executions[-1].datetime if self.executions else None
    
    def to_dict(self) -> dict:
        """Convierte a diccionario para serialización"""
        return {
            'symbol': self.symbol,
            'trade_type': self.trade_type.name,
            'start_datetime': self.start_datetime,
            'end_datetime': self.end_datetime,
            'entry_quantity': self.entry_quantity,
            'exit_quantity': self.exit_quantity,
            'entry_vwap': self.entry_vwap,
            'exit_vwap': self.exit_vwap,
            'gross_pnl': self.gross_pnl,
            'is_closed': self.is_closed,
            'n_executions': len(self.executions)
        }
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convierte las ejecuciones del trade a DataFrame"""
        return pd.DataFrame([e.raw_data for e in self.executions]).reset_index(drop=True)


class TradeBuilder:
    """Builder para construir trades desde ejecuciones"""
    
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        self.current_trade: Optional[Trade] = None
        self.completed_trades: list[Trade] = []
        self.position: float = 0.0
    
    def process_execution(self, execution: Execution) -> None:
        """
        Procesa una ejecución y actualiza trades.
        Maneja automáticamente cruces de cero.
        """
        new_position: float = self.position + execution.signed_quantity
        
        # Caso 1: Posición es 0, iniciar nuevo trade
        if abs(self.position) < 1e-9:
            if abs(execution.signed_quantity) > 1e-9:
                self._start_new_trade(execution=execution)
                self.position = new_position
            return
        
        # Caso 2: Mismo signo o cierre exacto (no cruza cero)
        if (np.sign(self.position) == np.sign(new_position)) or abs(new_position) < 1e-9:
            self.current_trade.add_execution(execution=execution)
            self.position = new_position
            
            # Si cierra exactamente, guardar trade
            if abs(self.position) < 1e-9:
                self._close_current_trade()
            return
        
        # Caso 3: Cruza cero - dividir ejecución
        qty_to_close: float = abs(self.position)
        
        close_exec, remaining_exec = execution.split(qty_to_take=qty_to_close)
        
        # Añadir parte que cierra
        self.current_trade.add_execution(execution=close_exec)
        self._close_current_trade()
        self.position = 0.0
        
        # Si queda cantidad, abrir nuevo trade
        if remaining_exec:
            self._start_new_trade(execution=remaining_exec)
            self.position = remaining_exec.signed_quantity
    
    def _start_new_trade(self, execution: Execution) -> None:
        """Inicia un nuevo trade"""
        self.current_trade = Trade(symbol=self.symbol)
        self.current_trade.add_execution(execution=execution)
    
    def _close_current_trade(self) -> None:
        """Cierra el trade actual y lo guarda"""
        if self.current_trade:
            self.completed_trades.append(self.current_trade)
            self.current_trade = None
    
    def finalize(self) -> list[Trade]:
        """Finaliza y retorna todos los trades"""
        # Guardar trade abierto si existe
        if self.current_trade:
            self._close_current_trade()
        
        return self.completed_trades


class TradeSplitter:
    """
    Clase principal para dividir ejecuciones en trades.
    Optimizada para rendimiento con procesamiento vectorizado donde sea posible.
    """
    
    def __init__(self, 
                 symbol_col: str = 'symb',
                 time_col: str = 'time',
                 price_col: str = 'price',
                 qty_col: str = 'qty',
                 side_col: str = 'B/S') -> None:
        self.symbol_col: str = symbol_col
        self.time_col: str = time_col
        self.price_col: str = price_col
        self.qty_col: str = qty_col
        self.side_col: str = side_col
    
    def split(self, df: pd.DataFrame) -> dict[str, list[Trade]]:
        """
        Divide DataFrame de ejecuciones en trades por símbolo.
        
        Args:
            df: DataFrame con columnas de ejecuciones
            
        Returns:
            dict[symbol -> list[Trade]]
        """
        self._validate_dataframe(df=df)
        
        # Parsear todas las ejecuciones una sola vez (vectorizado donde posible)
        executions_by_symbol: dict[str, list[Execution]] = self._parse_executions(df)
        
        # Procesar cada símbolo
        results: dict[str, list[Trade]] = {}
        for symbol, executions in executions_by_symbol.items():
            builder = TradeBuilder(symbol=symbol)
            
            for execution in executions:
                builder.process_execution(execution=execution)
            
            results[symbol] = builder.finalize()
        
        return results
    
    def _validate_dataframe(self, df: pd.DataFrame) -> None:
        """Valida que el DataFrame tenga las columnas necesarias"""
        required: list[str] = [self.symbol_col, self.time_col, self.price_col, 
                   self.qty_col, self.side_col]
        missing: list[str] = [col for col in required if col not in df.columns]
        
        if missing:
            raise ValueError(f"Faltan columnas requeridas: {missing}")
    
    def _parse_executions(self, df: pd.DataFrame) -> dict[str, list[Execution]]:
        """
        Parsea DataFrame en Executions agrupadas por símbolo.
        Optimizado con operaciones vectorizadas.
        """
        # Crear copia y parsear tiempos
        df = df.copy()
        df['_parsed_dt'] = pd.to_datetime(
            df[self.time_col].str.strip(), 
            format='%m/%d/%y %H:%M:%S'
        ).dt.tz_localize('UTC')
        
        # Ordenar una sola vez
        df = df.sort_values([self.symbol_col, '_parsed_dt']).reset_index(drop=True)
        
        # Agrupar y crear ejecuciones
        results: dict[str, list[Execution]] = {}
        for symbol, group in df.groupby(self.symbol_col, sort=False):
            results[symbol] = [
                Execution(
                    datetime=row['_parsed_dt'],
                    price=float(row[self.price_col]),
                    quantity=float(row[self.qty_col]),
                    side=TradeSide.from_string(row[self.side_col]),
                    raw_data=row
                )
                for _, row in group.iterrows()
            ]
        
        return results


class TradeSummaryReport:
    """Genera reportes de trades"""
    
    @staticmethod
    def print_summary(trades_by_symbol: dict[str, list[Trade]]) -> None:
        """Imprime resumen formateado de trades"""
        print(f"\n{'='*80}")
        print("RESUMEN DE TRADES")
        print(f"{'='*80}\n")
        
        total_trades: int = sum(len(trades) for trades in trades_by_symbol.values())
        total_symbols: int = len(trades_by_symbol)
        
        print(f"Total símbolos: {total_symbols}")
        print(f"Total trades: {total_trades}\n")
        
        for symbol, trades in trades_by_symbol.items():
            print(f"\n{symbol}: {len(trades)} trade(s)")
            print("-" * 80)
            
            for i, trade in enumerate(trades, 1):
                status = "✓ CERRADO" if trade.is_closed else "○ ABIERTO"
                print(f"\n  Trade #{i} {status}")
                print(f"    Tipo: {trade.trade_type.name}")
                print(f"    Inicio: {trade.start_datetime.strftime('%H:%M:%S')}")
                print(f"    Fin: {trade.end_datetime.strftime('%H:%M:%S')}")
                
                if trade.entry_vwap:
                    print(f"    Entry: {trade.entry_quantity:.0f} @ ${trade.entry_vwap:.4f}")
                if trade.exit_vwap:
                    print(f"    Exit: {trade.exit_quantity:.0f} @ ${trade.exit_vwap:.4f}")
                
                if trade.gross_pnl is not None:
                    print(f"    P&L bruto: ${trade.gross_pnl:+.2f}")
                
                print(f"    Ejecuciones: {len(trade.executions)}")
        
        print(f"\n{'='*80}\n")


class CSVImporter:
    """Importador de CSV a base de datos con validación y logging"""
    
    def __init__(self, current_app, trade_model, transaction_model, user_id: int) -> None:
        """
        Args:
            user_id: ID del usuario propietario de los trades
            commission_per_trade: Comisión por ejecución (default: $1.00)
        """
        self.user_id: int = user_id
        self.commission_per_trade: float = 0.0
        self.splitter = TradeSplitter()
        self.stats = ImportStats()
        self.current_app = current_app
        self.trade_model = trade_model
        self.transaction_model = transaction_model
    
    def import_from_file(self, file_path: str | Path, 
                       dry_run: bool = False) -> tuple[ImportStats, list]:
        """
        Importa trades desde CSV a base de datos.
        
        Args:
            file_path: Ruta al archivo
            dry_run: Si True, procesa pero no commitea a DB
            
        Returns:
            ImportStats con resumen de la importación
        """
        self.stats = ImportStats()
        
        # try:
        # 1. Leer y validar CSV
        df: pd.DataFrame = self._read_file(file_path=file_path)
        self.stats.total_executions = len(df)
        
        # 2. Dividir en trades
        trades_by_symbol: dict[str, list[Trade]] = self.splitter.split(df=df)
        
        # 3. Crear modelos de base de datos
        loged_trades: list = []
        for symbol, trades in trades_by_symbol.items():
            for trade in trades:
                try:
                    loged_trades.append(self._create_trade_in_db(trade=trade, dry_run=dry_run))
                    self.stats.trades_created += 1
                    
                    if trade.is_closed:
                        self.stats.closed_trades += 1
                    else:
                        self.stats.open_trades += 1
                        
                except Exception as e:
                    self.stats.errors.append(f"Error creando trade {symbol}: {str(e)}")
                    self.current_app.logger.error(f"Error importing trade: {e}", exc_info=True)
            
        # except Exception as e:
        #     self.stats.success = False
        #     self.stats.errors.append(f"Error general: {str(e)}")
        #     self.current_app.logger.error(f"Import failed: {e}", exc_info=True)
        #     raise
        
        return self.stats, loged_trades
    
    def _read_file(self, file_path: str | Path) -> pd.DataFrame:
        """Lee y valida CSV"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            if path.suffix.lower() == '.xlsx':
                df: pd.DataFrame = pd.read_excel(path)
            else:
                df: pd.DataFrame = pd.read_csv(path)
        except Exception as e:
            raise ValueError(f"Error reading file: {e}")
        
        # Validar columnas requeridas
        required: list[str] = ['symb', 'time', 'price', 'qty', 'B/S']
        missing: list[str] = [col for col in required if col not in df.columns]
        if missing:
            raise ValueError(f"Faltan columnas en CSV: {missing}")
        
        return df
    
    def _create_trade_in_db(self, trade: Trade, 
                           dry_run: bool=False):
        """
        Crea modelo Trade y sus Transactions en base de datos.
        
        Args:
            trade: Objeto Trade del splitter
            dry_run: Si True, no commitea
            
        Returns:
            TradeModel creado
        """
        # Calcular comisión total
        total_commission: float = len(trade.executions) * self.commission_per_trade
        
        # Calcular P&L neto (con comisiones)
        net_pnl: float = (trade.gross_pnl or 0.0) - total_commission
        
        # Crear Trade
        trade_model = self.trade_model(
            symbol=trade.symbol,
            entry_date=trade.start_datetime.date(),
            entry_time=trade.start_datetime.strftime('%H:%M:%S'),
            entry_price=trade.entry_vwap,
            quantity=trade.entry_quantity,
            trade_type=trade.trade_type.name,
            exit_date=trade.end_datetime.date() if trade.is_closed else None,
            exit_time=trade.end_datetime.strftime('%H:%M:%S') if trade.is_closed else None,
            exit_price=trade.exit_vwap if trade.is_closed else None,
            exit_quantity=trade.exit_quantity if trade.exit_quantity > 0 else None,
            commission=total_commission,
            profit_loss=net_pnl,
            strategy_id=None,
            user_id=self.user_id,
            # Campos opcionales - ajusta según necesites
            balance=None,  # Calcular si tienes balance inicial
            stop_loss=None,
            take_profit=None,
            description=self._generate_description(trade),
        )
        
        # Crear Transactions
        trade_model.transactions = [self._create_transaction(execution=execution) for execution in trade.executions]
        self.stats.transactions_created += len(trade.executions)
        
        return trade_model
    
    def _create_transaction(self, execution: Execution, 
                           trade_id:int=None):
        """Crea modelo Transaction desde Execution"""
        return self.transaction_model(
            date=execution.datetime.date(),
            time=execution.datetime.strftime('%H:%M:%S'),
            price=execution.price,
            quantity=execution.quantity,
            commission=self.commission_per_trade,
            type=execution.side.name,
            trade_id=trade_id
        )
    
    def _generate_description(self, trade: Trade) -> str:
        """Genera descripción automática del trade"""
        duration: timedelta = trade.end_datetime - trade.start_datetime
        minutes = int(duration.total_seconds() / 60)
        
        desc: str = f"{trade.trade_type.name} trade con {len(trade.executions)} ejecuciones"
        
        if trade.is_closed:
            desc += f", duración {minutes} minutos"
            if trade.gross_pnl:
                desc += f", P&L ${trade.gross_pnl:+.2f}"
        else:
            desc += " (ABIERTO)"
        
        return desc


class ImportStats:
    """Estadísticas de importación"""
    
    def __init__(self):
        self.success: bool = False
        self.total_executions: int = 0
        self.trades_created: int = 0
        self.closed_trades: int = 0
        self.open_trades: int = 0
        self.transactions_created: int = 0
        self.errors: list[str] = []
    
    def __str__(self) -> str:
        """Formato legible de estadísticas"""
        status = "✓ ÉXITO" if self.success else "✗ ERROR"
        
        report = [
            f"\n{'='*80}",
            f"REPORTE DE IMPORTACIÓN - {status}",
            f"{'='*80}",
            f"Ejecuciones procesadas: {self.total_executions}",
            f"Trades creados: {self.trades_created}",
            f"  - Cerrados: {self.closed_trades}",
            f"  - Abiertos: {self.open_trades}",
            f"Transacciones creadas: {self.transactions_created}",
        ]
        
        if self.errors:
            report.append(f"\nErrores ({len(self.errors)}):")
            for error in self.errors:
                report.append(f"  - {error}")
        
        report.append(f"{'='*80}\n")
        
        return "\n".join(report)


class BatchImporter:
    """Importador de múltiples archivos CSV"""
    
    def __init__(self, current_app, trade_model, transaction_model, user_id: int, db) -> None:
        self.user_id: int = user_id
        self.commission_per_trade: float = 0.0
        self.current_app = current_app
        self.trade_model = trade_model
        self.transaction_model = transaction_model
        self.db = db
    
    def import_directory(self, directory: str | Path,
                        pattern: str = "*.csv",
                        dry_run: bool = False) -> dict[str, ImportStats]:
        """
        Importa todos los CSVs de un directorio.
        
        Args:
            directory: Directorio con CSVs
            pattern: Patrón de archivos (default: "*.csv")
            dry_run: Modo prueba
            
        Returns:
            Dict[filename -> ImportStats]
        """
        directory = Path(directory)
        
        if not directory.exists() or not directory.is_dir():
            raise ValueError(f"Directorio inválido: {directory}")
        
        files: list[Path] = sorted(directory.glob(pattern))
        
        if not files:
            raise ValueError(f"No se encontraron archivos {pattern} en {directory}")
        
        results = {}
        
        for file in files:
            print(f"\nProcesando: {file.name}")
            
            importer = CSVImporter(current_app=self.current_app, trade_model=self.trade_model, 
                                   transaction_model=self.transaction_model, user_id=self.user_id, db=self.db)
            
            try:
                stats: ImportStats = importer.import_from_file(file_path=file, dry_run=dry_run)
                results[file.name] = stats
                print(stats)
                
            except Exception as e:
                print(f"ERROR: {e}")
                results[file.name] = ImportStats()
                results[file.name].errors.append(str(e))
        
        return results

# Ejemplo de uso
if __name__ == "__main__":
    # Cargar datos
    df: pd.DataFrame = pd.read_csv(filepath_or_buffer="2025-10-11.csv")
    
    # Crear splitter y procesar
    splitter = TradeSplitter()
    trades_by_symbol: dict[str, list[Trade]] = splitter.split(df)
    
    # Mostrar resumen
    TradeSummaryReport.print_summary(trades_by_symbol=trades_by_symbol)
    
    # Acceder a trades individuales
    for symbol, trades in trades_by_symbol.items():
        for trade in trades:
            # Convertir a dict si necesitas serializar
            trade_dict: dict = trade.to_dict()
            
            # O convertir ejecuciones a DataFrame
            executions_df: pd.DataFrame = trade.to_dataframe()

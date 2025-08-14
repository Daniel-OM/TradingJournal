
import os
import pytz
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import flash

from ..config import UPLOAD_FOLDER, ALLOWED_IMAGE_EXTENSIONS, ALLOWED_VIDEO_EXTENSIONS, MAX_IMAGE_SIZE, MAX_VIDEO_SIZE
from ..models import Trade, Candle
from ..src.yahoofinance import YahooTicker

def allowed_file(filename, allowed_extensions) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_files(files, file_type, trade_id) -> list:
    """
    Guarda los archivos subidos y devuelve las rutas
    """
    saved_paths: list = []
    
    if not files:
        return saved_paths
    
    # Crear directorio si no existe
    upload_path: str = os.path.join(UPLOAD_FOLDER, file_type, str(trade_id))
    os.makedirs(name=upload_path, exist_ok=True)
    
    allowed_extensions: set[str] = ALLOWED_IMAGE_EXTENSIONS if file_type == 'images' else ALLOWED_VIDEO_EXTENSIONS
    max_size = MAX_IMAGE_SIZE if file_type == 'images' else MAX_VIDEO_SIZE
    
    for i, file in enumerate(files):
        if file and file.filename != '':
            if allowed_file(filename=file.filename, allowed_extensions=allowed_extensions):
                # Verificar tamaño del archivo
                file.seek(0, 2)  # Ir al final del archivo
                file_size = file.tell()
                file.seek(0)  # Volver al inicio
                
                if file_size <= max_size:
                    # Generar nombre seguro y único
                    filename: str = secure_filename(filename=str(i) + '.' + file.filename.rsplit('.', 1)[1].lower())
                    
                    file_path: str = os.path.join(upload_path, filename)
                    file.save(file_path)
                    
                    # Guardar ruta relativa (sin static)
                    # relative_path: str = upload_path
                    saved_paths.append(file_path)
                else:
                    flash(f'El archivo {file.filename} es demasiado grande', 'warning')
            else:
                flash(f'Tipo de archivo no permitido: {file.filename}', 'warning')
    
    return saved_paths



def calculate_max_drawdown(trades: list[Trade]) -> int:
    """Calcular el maximum drawdown de una serie de trades"""
    if not trades:
        return 0
    
    # Calcular equity curve
    equity: list = []
    running_total = 0
    
    for trade in trades:
        running_total += trade.profit_loss
        equity.append(running_total)
    
    if not equity:
        return 0
    
    # Calcular drawdown
    peak = equity[0]
    max_dd: int = 0
    
    for value in equity:
        if value > peak:
            peak = value
        
        drawdown = (peak - value) / peak * 100 if peak != 0 else 0
        max_dd = max(max_dd, drawdown)
    
    return max_dd


def download_candles(db, symbol:str, config:dict[str, datetime|str]):
    '''
    symbol: str
        Symbol of the asset.
    config: list[list]
        List with the configurations. Eg:
        [{'start': dt.datetime(2024,07,31, 0, 0, 0), 'end': dt.datetime(2025,07,31, 0, 0, 0), 'timeframe': '1d'}]
    '''
    try:
        yf = YahooTicker(symbol)
        data = []
        for conf in config:
            data.append([conf['timeframe'], yf.getPrice(start=conf['start'], end=conf['end'], timeframe=conf['timeframe'], df=True)])
            db.session.query(Candle).filter(Candle.symbol == symbol, Candle.date >= conf['start'], Candle.date <= conf['end'], Candle.timeframe == conf['timeframe']).delete(synchronize_session=False)

        db.session.commit()

        candle_objs = []
        for tf, candles in data:
            if hasattr(candles, 'iterrows'):
                candle_objs += [
                    Candle(
                        symbol=symbol,
                        date=row['date'] if 'date' in row else idx, # .strftime('%Y-%m-%d %H:%M:%S%z')
                        open=row['open'],
                        high=row['high'],
                        low=row['low'],
                        close=row['close'],
                        volume=row.get('volume', None),
                        session=row.get('session', 'REG'),
                        timeframe=tf
                    ) for idx, row in candles.iterrows()
                ]
            elif isinstance(candles, list):
                candle_objs += [
                    Candle(
                        symbol=symbol,
                        date=row['date'], # .strftime('%Y-%m-%d %H:%M:%S%z'),
                        open=row['open'],
                        high=row['high'],
                        low=row['low'],
                        close=row['close'],
                        volume=row.get('volume', None),
                        session=row.get('session', 'REG'),
                        timeframe=tf
                    ) for row in candles
                ]

        if candle_objs:
            db.session.bulk_save_objects(candle_objs)
            db.session.commit()

    except Exception as e:
        print(f"Error descargando velas para {symbol}: {e}")


def utcToLocal(date:str, time:str, tz:str='Europe/Madrid', mode:str='date'):
    
    # Crear objeto datetime en UTC
    dt_utc = datetime.fromisoformat(f"{date} {time}")
    # Convertir a zona local
    dt_local = pytz.timezone(zone=pytz.UTC).localize(dt_utc).astimezone(tz=pytz.timezone(zone=tz))

    if mode == 'time':
        return dt_local.strftime("%H:%M:%S")
    elif mode == 'date':
        return dt_local.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return dt_local


def localToUtc(date:str, time:str, tz:str='Europe/Madrid', mode:str='date'):
    """
    Convierte una hora en Madrid a UTC para una fecha específica
    
    Args:
        date: Fecha en formato "YYYY-MM-DD"
        time: Hora en formato "HH:MM:SS" o "HH:MM"
        tz: str
        mode: str
            Can be 'date' or 'time'.
    
    Returns:
        Hora en UTC como string
    """
    
    # Combinar fecha y hora
    dt_naive: datetime = datetime.fromisoformat(f"{date} {time}")
    # Convertir a UTC
    dt_utc: datetime = pytz.timezone(zone=tz).localize(dt=dt_naive).astimezone(tz=pytz.UTC)

    if mode == 'time':
        return dt_utc.strftime("%H:%M:%S")
    elif mode == 'date':
        return dt_utc.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return dt_utc

import os

from werkzeug.utils import secure_filename
from flask import flash

from ..config import UPLOAD_FOLDER, ALLOWED_IMAGE_EXTENSIONS, ALLOWED_VIDEO_EXTENSIONS, MAX_IMAGE_SIZE, MAX_VIDEO_SIZE
from ..models import Trade

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

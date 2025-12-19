#!/usr/bin/env python3
"""
Script para inicializar la base de datos con datos de ejemplo.
Uso: python init_db.py
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.models.models import User, Strategy, Trade, Watchlist, WatchlistEntry
from app.core.security import hash_password
from datetime import datetime, timedelta
import random


def init_db():
    """Inicializar la base de datos con datos de ejemplo"""
    
    try:
        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        print("✓ Tablas creadas")
    except Exception as e:
        print(f"✗ Error creando tablas: {e}")
        return
    
    db = SessionLocal()
    
    try:
        # Verificar si ya existe un usuario
        existing_user = db.query(User).filter(User.username == "trader").first()
        if existing_user:
            print("✓ Usuario 'trader' ya existe")
            db.close()
            return
        
        # Crear usuario de ejemplo
        user = User(
            username="trader",
            email="trader@example.com",
            hashed_password=hash_password("password123")
        )
        db.add(user)
        db.flush()  # Para obtener el ID sin hacer commit
        
        print("✓ Usuario creado: trader / password123")
        
        # Crear estrategias de ejemplo
        strategies = [
            Strategy(
                user_id=user.id,
                name="Momentum Trading",
                description="Trading basado en momentum de precios",
                is_active=True
            ),
            Strategy(
                user_id=user.id,
                name="Support & Resistance",
                description="Trading en niveles de soporte y resistencia",
                is_active=True
            ),
            Strategy(
                user_id=user.id,
                name="Breakout Trading",
                description="Trading de rupturas de rangos",
                is_active=False
            ),
        ]
        db.add_all(strategies)
        db.flush()
        
        print(f"✓ {len(strategies)} estrategias creadas")
        
        # Crear trades de ejemplo
        symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NFLX", "NVDA"]
        base_date = datetime.now() - timedelta(days=90)
        
        trades = []
        for i in range(20):
            symbol = random.choice(symbols)
            entry_date = base_date + timedelta(days=random.randint(0, 90))
            exit_date = entry_date + timedelta(days=random.randint(1, 5))
            entry_price = random.uniform(100, 500)
            exit_price = entry_price * random.uniform(0.95, 1.05)
            quantity = random.randint(1, 100)
            exit_quantity = quantity
            profit_loss = (exit_price - entry_price) * quantity
            commission = random.uniform(5, 50)
            
            trade = Trade(
                user_id=user.id,
                symbol=symbol,
                entry_date=entry_date,
                entry_price=entry_price,
                entry_time=f"{random.randint(9, 16)}:{random.randint(0, 59):02d}",
                quantity=quantity,
                trade_type=random.choice(["LONG", "SHORT"]),
                exit_date=exit_date if random.random() > 0.3 else None,
                exit_price=exit_price if random.random() > 0.3 else None,
                exit_time=f"{random.randint(9, 16)}:{random.randint(0, 59):02d}" if random.random() > 0.3 else None,
                exit_quantity=exit_quantity if random.random() > 0.3 else None,
                profit_loss=profit_loss if random.random() > 0.3 else None,
                commission=commission,
                strategy_id=random.choice(strategies).id if random.random() > 0.5 else None,
                description=f"Trade de {symbol} - Ejemplo {i+1}",
                hashtags="#momentum #daytrading" if random.random() > 0.5 else "#swing #technical",
                stop_loss=entry_price * 0.95,
                take_profit=entry_price * 1.05,
            )
            trades.append(trade)
        
        db.add_all(trades)
        db.flush()
        
        print(f"✓ {len(trades)} trades creados")
        
        # Crear watchlists de ejemplo
        watchlists = [
            Watchlist(
                user_id=user.id,
                name="Tech Stocks",
                description="Acciones tecnológicas principales",
                is_active=True
            ),
            Watchlist(
                user_id=user.id,
                name="Day Trading Watch",
                description="Acciones para day trading",
                is_active=True
            ),
        ]
        db.add_all(watchlists)
        db.flush()
        
        print(f"✓ {len(watchlists)} watchlists creadas")
        
        # Crear entradas de watchlist
        watchlist_entries = []
        for watchlist in watchlists:
            for symbol in random.sample(symbols, k=4):
                entry = WatchlistEntry(
                    watchlist_id=watchlist.id,
                    symbol=symbol,
                    date=datetime.now(),
                    entry_price=random.uniform(100, 500),
                    reason=f"Monitoreo de {symbol} para setup de {watchlist.name}",
                    notes="Vigilar nivel de resistencia en 150"
                )
                watchlist_entries.append(entry)
        
        db.add_all(watchlist_entries)
        
        print(f"✓ {len(watchlist_entries)} entradas de watchlist creadas")
        
        # Commit de todos los cambios
        db.commit()
        
        print("\n" + "="*50)
        print("✓ Base de datos inicializada exitosamente!")
        print("="*50)
        print("\nCredenciales de ejemplo:")
        print("  Usuario: trader")
        print("  Email: trader@example.com")
        print("  Contraseña: password123")
        print("\nConexión:")
        print("  URL: http://localhost:3000")
        print("  Docs: http://localhost:3000/docs")
        print("\nPróximos pasos:")
        print("  1. Ejecutar: uvicorn app.main:app --reload")
        print("  2. Abre el navegador en: http://localhost:3000/docs")
        print("  3. Haz login con las credenciales anteriores")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error al inicializar BD: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()

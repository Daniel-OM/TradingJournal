import pytz
from datetime import date, time, datetime, timedelta
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models import Trade, Candle

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from yahoofinance import YahooTicker


# TODO: Add all the candles needed for the charts of the trades already registered

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instance', 'trading_journal.db'))
engine = create_engine(f'sqlite:///{db_path}')
Session = sessionmaker(bind=engine)
session = Session()


def getTradesCandles():
    trades: List[Trade] = session.query(Trade).all()

    for trade in trades:

        today = trade.exit_date or date.today()
        one_year_ago = trade.entry_date - timedelta(days=365)
        week_ago = trade.entry_date - timedelta(days=5)
        symbol = trade.symbol
        # Descargar velas con Yahoo Finance
        yf = YahooTicker(symbol)
        yearly_candles = yf.getPrice(start=int(datetime.combine(one_year_ago, time(0, 0, 0)).timestamp()), # , datetime.min.time()
                                    end=int(datetime.combine(today, time(23, 59, 59)).timestamp()), 
                                    timeframe='1d', df=True)
        intraday_candles = yf.getPrice(start=int(datetime.combine(week_ago, time(0, 0, 0)).timestamp()), 
                                        end=int(datetime.combine(today, time(23, 59, 59)).timestamp()), 
                                        timeframe='1m', df=True)
        print(yearly_candles.head(3), intraday_candles.head(3))
        # Eliminar todas las velas existentes para ese símbolo y rango de fechas
        session.query(Candle).filter(Candle.symbol == symbol, Candle.date >= one_year_ago, Candle.date <= today, Candle.timeframe == '1d').delete(synchronize_session=False)
        session.query(Candle).filter(Candle.symbol == symbol, Candle.date >= datetime.combine(week_ago, time(0, 0, 0)), Candle.date <= datetime.combine(today, time(23, 59, 59)), Candle.timeframe == '1m').delete(synchronize_session=False)
        session.commit()

        candle_objs = []
        for tf, candles in [['1d', yearly_candles], ['1m', intraday_candles]]:
            if hasattr(candles, 'iterrows'):
                candle_objs += [
                    Candle(
                        symbol=symbol,
                        date=row['date'].strftime('%Y-%m-%d %H:%M:%S%z') if 'date' in row else idx,
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
                        date=row['date'].strftime('%Y-%m-%d %H:%M:%S%z'),
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
            session.bulk_save_objects(candle_objs)
            session.commit()

def utcToLocal(date:str, time:str, tz:str='Europe/Madrid', mode:str='date'):
    
    # Crear objeto datetime en UTC
    dt_utc = datetime.fromisoformat(f"{date} {time}")
    # Convertir a zona local
    dt_local = pytz.timezone(zone='UTC').localize(dt_utc).astimezone(tz=pytz.timezone(zone=tz))

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
    dt_naive = datetime.fromisoformat(f"{date} {time}")
    # Convertir a UTC
    dt_utc = pytz.timezone(zone=tz).localize(dt=dt_naive).astimezone(tz=pytz.UTC)

    if mode == 'time':
        return dt_utc.strftime("%H:%M:%S")
    elif mode == 'date':
        return dt_utc.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return dt_utc
    
def changeTransactionTimezones():

    trades: List[Trade] = session.query(Trade).all()
    for trade in trades:
        
        trade.entry_time = localToUtc(date=trade.entry_date, time=trade.entry_time, tz='Europe/Madrid', mode='time')
        trade.exit_time = localToUtc(date=trade.exit_date, time=trade.exit_time, tz='Europe/Madrid', mode='time')
        for trans in trade.transactions:
            trans.time = localToUtc(date=trans.date, time=trans.time, tz='Europe/Madrid', mode='time')

    session.commit()

if __name__ == '__main__':

    if False:
        trades: List[Trade] = session.query(Trade).all()

        for trade in trades[-5:]:

            today = trade.exit_date or date.today()
            one_year_ago = trade.entry_date - timedelta(days=365)
            week_ago = trade.entry_date - timedelta(days=5)
            symbol = trade.symbol
            # Descargar velas con Yahoo Finance
            yf = YahooTicker(symbol)
            yearly_candles = yf.getPrice(start=int(datetime.combine(one_year_ago, time(0, 0, 0)).timestamp()), # , datetime.min.time()
                                        end=int(datetime.combine(today, time(23, 59, 59)).timestamp()), 
                                        timeframe='1d', df=True)
            intraday_candles = yf.getPrice(start=int(datetime.combine(week_ago, time(0, 0, 0)).timestamp()), 
                                            end=int(datetime.combine(today, time(23, 59, 59)).timestamp()), 
                                            timeframe='1m', df=True)
            print(yearly_candles.head(3), intraday_candles.head(3))
            # Eliminar todas las velas existentes para ese símbolo y rango de fechas
            session.query(Candle).filter(Candle.symbol == symbol, Candle.date >= one_year_ago, Candle.date <= today, Candle.timeframe == '1d').delete(synchronize_session=False)
            session.query(Candle).filter(Candle.symbol == symbol, Candle.date >= datetime.combine(week_ago, time(0, 0, 0)), Candle.date <= datetime.combine(today, time(23, 59, 59)), Candle.timeframe == '1m').delete(synchronize_session=False)
            session.commit()
            
            candle_objs = []
            for tf, candles in [['1d', yearly_candles], ['1m', intraday_candles]]:
                if hasattr(candles, 'iterrows'):
                    candle_objs += [
                        Candle(
                            symbol=symbol,
                            date=row['date'].strftime('%Y-%m-%d %H:%M:%S%z') if 'date' in row else idx,
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
                            date=row['date'].strftime('%Y-%m-%d %H:%M:%S%z'),
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
                session.bulk_save_objects(candle_objs)
                session.commit()

            
    elif False:
        getTradesCandles()

    changeTransactionTimezones()
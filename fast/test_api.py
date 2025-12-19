#!/usr/bin/env python3
"""
Script de testing para la API de Trading Journal
Uso: python test_api.py
"""

import requests
import json
from typing import Optional

BASE_URL = "http://localhost:3000/api/v1"
ACCESS_TOKEN = None


def print_response(response: requests.Response, title: str = ""):
    """Imprime la respuesta de forma legible"""
    print(f"\n{'='*60}")
    if title:
        print(f"📌 {title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print(response.text)


def test_register():
    """Prueba el registro de usuario"""
    global ACCESS_TOKEN
    
    data = {
        "username": "testtrader",
        "email": "testtrader@example.com",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    print_response(response, "REGISTRO DE USUARIO")
    
    return response.status_code == 200


def test_login():
    """Prueba el login"""
    global ACCESS_TOKEN
    
    data = {
        "username": "testtrader",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=data)
    print_response(response, "LOGIN")
    
    if response.status_code == 200:
        ACCESS_TOKEN = response.json()["access_token"]
        return True
    return False


def get_headers():
    """Retorna headers con el token de autorización"""
    return {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }


def test_create_strategy():
    """Prueba crear una estrategia"""
    data = {
        "name": "Test Strategy",
        "description": "Una estrategia de prueba",
        "is_active": True
    }
    
    response = requests.post(
        f"{BASE_URL}/strategies",
        json=data,
        headers=get_headers()
    )
    print_response(response, "CREAR ESTRATEGIA")
    
    if response.status_code == 200:
        return response.json()["id"]
    return None


def test_create_trade(strategy_id: Optional[int] = None):
    """Prueba crear un trade"""
    data = {
        "symbol": "AAPL",
        "entry_date": "2024-01-15",
        "entry_price": 150.50,
        "entry_time": "09:30",
        "quantity": 100,
        "trade_type": "LONG",
        "exit_date": "2024-01-16",
        "exit_price": 152.00,
        "exit_time": "14:00",
        "exit_quantity": 100,
        "profit_loss": 150.00,
        "commission": 10.00,
        "description": "Trade de prueba",
        "strategy_id": strategy_id
    }
    
    response = requests.post(
        f"{BASE_URL}/trades",
        json=data,
        headers=get_headers()
    )
    print_response(response, "CREAR TRADE")
    
    if response.status_code == 200:
        return response.json()["id"]
    return None


def test_list_trades():
    """Prueba listar trades"""
    response = requests.get(
        f"{BASE_URL}/trades",
        headers=get_headers()
    )
    print_response(response, "LISTAR TRADES")


def test_get_trade(trade_id: int):
    """Prueba obtener un trade específico"""
    response = requests.get(
        f"{BASE_URL}/trades/{trade_id}",
        headers=get_headers()
    )
    print_response(response, "OBTENER TRADE")


def test_update_trade(trade_id: int):
    """Prueba actualizar un trade"""
    data = {
        "description": "Trade actualizado en la prueba"
    }
    
    response = requests.put(
        f"{BASE_URL}/trades/{trade_id}",
        json=data,
        headers=get_headers()
    )
    print_response(response, "ACTUALIZAR TRADE")


def test_delete_trade(trade_id: int):
    """Prueba eliminar un trade"""
    response = requests.delete(
        f"{BASE_URL}/trades/{trade_id}",
        headers=get_headers()
    )
    print_response(response, "ELIMINAR TRADE")


def test_performance_stats():
    """Prueba obtener estadísticas de performance"""
    response = requests.get(
        f"{BASE_URL}/performance/stats",
        headers=get_headers()
    )
    print_response(response, "ESTADÍSTICAS DE PERFORMANCE")


def test_performance_symbols():
    """Prueba obtener performance por símbolo"""
    response = requests.get(
        f"{BASE_URL}/performance/symbols",
        headers=get_headers()
    )
    print_response(response, "PERFORMANCE POR SÍMBOLO")


def test_create_watchlist():
    """Prueba crear una watchlist"""
    data = {
        "name": "Tech Stocks",
        "description": "Acciones tecnológicas principales",
        "is_active": True
    }
    
    response = requests.post(
        f"{BASE_URL}/watchlists",
        json=data,
        headers=get_headers()
    )
    print_response(response, "CREAR WATCHLIST")
    
    if response.status_code == 200:
        return response.json()["id"]
    return None


def test_list_watchlists():
    """Prueba listar watchlists"""
    response = requests.get(
        f"{BASE_URL}/watchlists",
        headers=get_headers()
    )
    print_response(response, "LISTAR WATCHLISTS")


def run_all_tests():
    """Ejecuta todos los tests"""
    print("\n🚀 Iniciando pruebas de API Trading Journal\n")
    
    # Test auth
    if not test_register():
        print("⚠️  El usuario probablemente ya existe, continuando...")
    
    if not test_login():
        print("❌ Login fallido!")
        return
    
    print("\n✅ Autenticación exitosa!\n")
    
    # Test estrategias
    strategy_id = test_create_strategy()
    
    # Test trades
    trade_id = test_create_trade(strategy_id)
    
    if trade_id:
        test_list_trades()
        test_get_trade(trade_id)
        test_update_trade(trade_id)
        test_performance_stats()
        test_performance_symbols()
        test_delete_trade(trade_id)
    
    # Test watchlists
    watchlist_id = test_create_watchlist()
    if watchlist_id:
        test_list_watchlists()
    
    print("\n" + "="*60)
    print("✅ Pruebas completadas!")
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar a http://localhost:3000")
        print("   Asegúrate de que el servidor está ejecutándose:")
        print("   uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")

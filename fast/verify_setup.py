#!/usr/bin/env python3
"""
🔍 Script de Verificación del Proyecto FastAPI
Verifica que todo esté correctamente instalado y configurado
"""

import os
import sys
import subprocess
from pathlib import Path


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")


def print_check(item, status, message=""):
    icon = f"{Colors.GREEN}✓{Colors.END}" if status else f"{Colors.RED}✗{Colors.END}"
    print(f"  {icon} {item}")
    if message:
        print(f"    → {message}")


def check_python_version():
    """Verifica versión de Python"""
    print_header("1. Python Version")
    version = sys.version_info
    required = (3, 8)
    status = version >= required
    
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    print_check(
        f"Python {version_str}",
        status,
        f"{'OK' if status else f'Requiere 3.8+, tienes {version_str}'}"
    )
    return status


def check_venv():
    """Verifica que estamos en un venv"""
    print_header("2. Virtual Environment")
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    print_check(
        "Virtual environment activo",
        in_venv,
        "Asegúrate de activar venv" if not in_venv else f"Usando: {sys.prefix}"
    )
    return in_venv


def check_files():
    """Verifica archivos principales"""
    print_header("3. Project Files")
    
    required_files = [
        "app/__init__.py",
        "app/main.py",
        "app/core/__init__.py",
        "app/core/config.py",
        "app/core/security.py",
        "app/db/__init__.py",
        "app/db/database.py",
        "app/models/__init__.py",
        "app/models/models.py",
        "app/schemas/__init__.py",
        "app/schemas/schemas.py",
        "app/services/__init__.py",
        "app/services/performance.py",
        "app/api/__init__.py",
        "app/api/v1/__init__.py",
        "app/api/v1/endpoints.py",
        "requirements.txt",
        ".env.example",
        "README.md",
    ]
    
    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        exists = path.exists()
        all_exist = all_exist and exists
        print_check(file_path, exists)
    
    return all_exist


def check_dependencies():
    """Verifica dependencias instaladas"""
    print_header("4. Dependencies")
    
    required_packages = {
        "fastapi": "FastAPI",
        "uvicorn": "Uvicorn (ASGI server)",
        "sqlalchemy": "SQLAlchemy (ORM)",
        "pydantic": "Pydantic (Validation)",
        "pydantic_settings": "Pydantic Settings",
        "jose": "python-jose (JWT)",
        "passlib": "Passlib (Password hashing)",
        "multipart": "python-multipart",
    }
    
    all_installed = True
    for package, name in required_packages.items():
        try:
            __import__(package)
            print_check(name, True)
        except ImportError:
            print_check(name, False, f"Falta: pip install {package}")
            all_installed = False
    
    return all_installed


def check_env():
    """Verifica configuración .env"""
    print_header("5. Environment Configuration")
    
    env_exists = Path(".env").exists()
    env_example_exists = Path(".env.example").exists()
    
    print_check(".env existe", env_exists, 
                "Copia .env.example: cp .env.example .env" if not env_exists else "OK")
    print_check(".env.example existe", env_example_exists)
    
    if env_exists:
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = [
            "DATABASE_URL",
            "SECRET_KEY",
            "ALGORITHM",
            "ACCESS_TOKEN_EXPIRE_MINUTES",
        ]
        
        all_vars = True
        for var in required_vars:
            value = os.getenv(var)
            all_vars = all_vars and (value is not None)
            print_check(f"  {var}", value is not None)
        
        return env_exists and all_vars
    
    return env_exists


def check_database():
    """Verifica base de datos"""
    print_header("6. Database")
    
    db_file = Path("trading_journal.db")
    db_exists = db_file.exists()
    
    print_check("trading_journal.db existe", db_exists,
                "Ejecuta: python init_db.py" if not db_exists else "OK")
    
    return db_exists


def check_imports():
    """Verifica que se puedan importar módulos"""
    print_header("7. Module Imports")
    
    imports_ok = True
    modules = [
        ("app.main", "Main app"),
        ("app.core.config", "Config"),
        ("app.core.security", "Security"),
        ("app.db.database", "Database"),
        ("app.models.models", "Models"),
        ("app.schemas.schemas", "Schemas"),
        ("app.services.performance", "Performance"),
        ("app.api.v1.endpoints", "Endpoints"),
    ]
    
    for module, name in modules:
        try:
            __import__(module)
            print_check(name, True)
        except Exception as e:
            print_check(name, False, str(e)[:50])
            imports_ok = False
    
    return imports_ok


def check_server():
    """Intenta conectar al servidor (si está corriendo)"""
    print_header("8. Server Status")
    
    try:
        import requests
        try:
            response = requests.get("http://localhost:3000/health", timeout=2)
            print_check("Servidor corriendo", True, "http://localhost:3000")
            print_check("Health endpoint", response.status_code == 200)
            return True
        except requests.exceptions.ConnectionError:
            print_check("Servidor corriendo", False,
                       "Inicia con: uvicorn app.main:app --reload")
            return False
    except ImportError:
        print_check("requests library", False, "pip install requests")
        return False


def print_summary(results):
    """Imprime resumen"""
    print_header("✨ RESUMEN")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"  Verificaciones: {Colors.BOLD}{passed}/{total}{Colors.END}")
    print()
    
    if passed == total:
        print(f"  {Colors.GREEN}{Colors.BOLD}✓ ¡TODO OK!{Colors.END}")
        print()
        print("  Próximos pasos:")
        print("  1. uvicorn app.main:app --reload")
        print("  2. http://localhost:3000/docs")
        print("  3. python test_api.py")
        return True
    else:
        print(f"  {Colors.RED}{Colors.BOLD}✗ Hay problemas que resolver{Colors.END}")
        print()
        print("  Por favor, sigue las instrucciones arriba")
        return False


def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  🔍 Trading Journal FastAPI - Health Check              ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(Colors.END)
    
    results = {
        "Python version": check_python_version(),
        "Virtual environment": check_venv(),
        "Project files": check_files(),
        "Dependencies": check_dependencies(),
        "Environment config": check_env(),
        "Database": check_database(),
        "Module imports": check_imports(),
        "Server running": check_server(),
    }
    
    success = print_summary(results)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

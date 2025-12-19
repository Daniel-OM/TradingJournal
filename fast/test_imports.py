#!/usr/bin/env python3
"""
🔍 Test rápido de imports
Verifica que todos los módulos pueden importarse correctamente
"""

print("Testing imports...")

try:
    print("✓ Importando app.core.config...")
    from app.core.config import settings
    print(f"  - APP_NAME: {settings.APP_NAME}")
    print(f"  - DATABASE_URL: {settings.DATABASE_URL}")
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

try:
    print("✓ Importando app.core.security...")
    from app.core.security import hash_password, verify_password
    print(f"  - hash_password: OK")
    print(f"  - verify_password: OK")
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

try:
    print("✓ Importando app.db.database...")
    from app.db.database import SessionLocal, engine, Base
    print(f"  - SessionLocal: OK")
    print(f"  - engine: OK")
    print(f"  - Base: OK")
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

try:
    print("✓ Importando app.models.models...")
    from app.models.models import User, Trade, Strategy
    print(f"  - User: OK")
    print(f"  - Trade: OK")
    print(f"  - Strategy: OK")
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

try:
    print("✓ Importando app.schemas.schemas...")
    from app.schemas.schemas import UserCreate, TradeCreate
    print(f"  - UserCreate: OK")
    print(f"  - TradeCreate: OK")
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

try:
    print("✓ Importando app.api.v1.endpoints...")
    from app.api.v1 import endpoints
    print(f"  - endpoints: OK")
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

try:
    print("✓ Importando app.main...")
    from app.main import app
    print(f"  - FastAPI app: OK")
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

print("\n" + "="*50)
print("✅ Todos los imports funcionan correctamente!")
print("="*50)

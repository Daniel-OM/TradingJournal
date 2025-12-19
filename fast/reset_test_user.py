#!/usr/bin/env python3
"""
Script para resetear usuario de prueba con hash argon2 correcto
"""
import sys
from app.db.database import SessionLocal, Base, engine
from app.models import User
from app.core.security import hash_password

def reset_test_user():
    """Eliminar y recrear usuario de prueba"""
    
    # Crear tablas si no existen
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Eliminar usuario existente
        existing_user = db.query(User).filter(User.username == "test").first()
        if existing_user:
            db.delete(existing_user)
            db.commit()
            print("✓ Usuario anterior eliminado")
        
        # Crear nuevo usuario con hash correcto
        new_user = User(
            username="test",
            email="test@example.com",
            hashed_password=hash_password("test123")
        )
        db.add(new_user)
        db.commit()
        print("✓ Usuario 'test' creado con contraseña 'test123'")
        print(f"✓ Hash almacenado: {new_user.hashed_password[:20]}...")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    reset_test_user()

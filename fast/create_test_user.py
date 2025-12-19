#!/usr/bin/env python
"""
Script para crear un usuario de prueba en la base de datos
Uso: python create_test_user.py
"""

from app.core.security import hash_password
from app.db.database import SessionLocal, Base, engine
from app.models import User

def create_test_user():
    """Crea un usuario de prueba para desarrollo"""
    # Crear tablas
    Base.metadata.create_all(bind=engine)
    
    # Crear sesión
    db = SessionLocal()
    
    try:
        # Verificar si el usuario ya existe
        existing = db.query(User).filter(User.username == 'test').first()
        if existing:
            print('✓ Usuario de prueba ya existe')
            print(f'  Username: test')
            print(f'  Password: test123')
            return
        
        # Crear usuario de prueba
        user = User(
            username='test',
            email='test@example.com',
            hashed_password=hash_password('test123')
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print('✓ Usuario de prueba creado exitosamente!')
        print(f'  Username: test')
        print(f'  Password: test123')
        print(f'  Email: test@example.com')
        print(f'  ID: {user.id}')
        
    except Exception as e:
        print(f'✗ Error al crear usuario: {e}')
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    create_test_user()

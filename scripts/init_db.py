"""
Script para crear las tablas en la base de datos.
"""

from app.database import create_db_and_tables

if __name__ == "__main__":
    print("Creando tablas...")
    create_db_and_tables()
    print("Listo.")
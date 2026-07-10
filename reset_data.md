# 1. Supprime complètement la base de données
rm db.sqlite3

# 2. Supprime TOUS les fichiers de migrations
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# 3. Recrée tout depuis zéro
python manage.py migrate


# 4. Superuser
python manage.py createsuperuser

je dois faire un pip install psycopg2-binary pour que ça fonctionne avec postgresql
en suite pip freeze > requirements.txt

#----------------------------------------------------------------------------------------------------------------------------
# Script universel qui détecte le moteur de base de données
from django.db import connection
import sqlite3
import os

def reset_database_sequences():
    """🎯 Réinitialise toutes les séquences selon le moteur DB"""
    
    db_engine = connection.vendor
    print(f"🔧 Moteur de base détecté: {db_engine}")
    
    if db_engine == 'sqlite':
        reset_sqlite_sequences()
        print(f'sqlite{db_engine} séquences supprimé')
    elif db_engine == 'postgresql':
        reset_postgresql_sequences()
    elif db_engine == 'mysql':
        reset_mysql_sequences()
    else:
        print(f"❌ Moteur {db_engine} non supporté")

def reset_sqlite_sequences():
    """🗑️ Nettoie SQLite complètement"""
    db_path = 'db.sqlite3'
    if os.path.exists(db_path):
        os.remove(db_path)
        print("✅ db.sqlite3 supprimé - Recréez avec: python manage.py migrate")
    else:
        print("ℹ️ db.sqlite3 n'existe pas déjà")

def reset_postgresql_sequences():
    """🔄 Réinitialise les séquences PostgreSQL"""
    with connection.cursor() as cursor:
        # Réinitialiser toutes les séquences
        cursor.execute("""
            SELECT c.relname
            FROM pg_class c
            WHERE c.relkind = 'S'
        """)
        sequences = [row[0] for row in cursor.fetchall()]
        
        for seq in sequences:
            cursor.execute(f"ALTER SEQUENCE {seq} RESTART WITH 1;")
            print(f"✅ {seq} réinitialisée")
        
        print(f"🎉 {len(sequences)} séquences PostgreSQL réinitialisées")

def reset_mysql_sequences():
    """🔄 Réinitialise les AUTO_INCREMENT MySQL"""
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES;")
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in tables:
            cursor.execute(f"ALTER TABLE {table} AUTO_INCREMENT = 1;")
            print(f"✅ {table} réinitialisé")
        
        print(f"🎉 {len(tables)} tables MySQL réinitialisées")

# 🚀 EXÉCUTION
#if __name__ == "__main__":


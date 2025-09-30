import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Obtener todas las tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("📊 TABLAS CREADAS EN LA BASE DE DATOS SQLite:")
print("=" * 50)

for table in tables:
    table_name = table[0]
    print(f"✅ {table_name}")
    
    # Contar registros en cada tabla
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"   └─ Registros: {count}")
    except:
        print(f"   └─ Error al contar registros")

print(f"\n📈 TOTAL DE TABLAS: {len(tables)}")

# Cerrar conexión
conn.close()
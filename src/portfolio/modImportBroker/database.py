import sqlite3
import requests
import datetime

# Configuración de la base de datos SQLite
def init_db():
    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS operaciones (
            id INTEGER PRIMARY KEY,
            fecha TEXT,
            descripcion TEXT,
            cantidad REAL,
            precio REAL
        )
    """)
    conn.commit()
    conn.close()

# Guardar operaciones en la caché
def guardar_en_cache(operaciones):
    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()
    for operacion in operaciones:
        cursor.execute("""
            INSERT OR IGNORE INTO operaciones (id, fecha, descripcion, cantidad, precio)
            VALUES (?, ?, ?, ?, ?)
        """, (operacion['id'], operacion['fecha'], operacion['descripcion'], operacion['cantidad'], operacion['precio']))
    conn.commit()
    conn.close()

# Verificar qué datos están cacheados
def obtener_ids_cacheados():
    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM operaciones")
    ids = {row[0] for row in cursor.fetchall()}
    conn.close()
    return ids

# Obtener datos de la API
def obtener_operaciones(api_url, token):
    response = requests.get(api_url, headers={"Authorization": f"Bearer {token}"})
    response.raise_for_status()
    return response.json()

# Función principal
def sincronizar_operaciones(api_url, token):
    init_db()  # Inicializa la base de datos si no existe
    cacheados = obtener_ids_cacheados()  # Obtiene los IDs cacheados
    nuevas_operaciones = []
    todas_operaciones = obtener_operaciones(api_url, token)  # Obtén todas las operaciones

    for operacion in todas_operaciones:
        if operacion['id'] not in cacheados:
            nuevas_operaciones.append(operacion)

    if nuevas_operaciones:
        guardar_en_cache(nuevas_operaciones)  # Guarda las nuevas operaciones en la caché
        print(f"{len(nuevas_operaciones)} nuevas operaciones cacheadas.")
    else:
        print("No hay nuevas operaciones para cachear.")

# Ejemplo de uso
API_URL = "https://api.invertironline.com/api/v2/operaciones"  # URL de ejemplo
TOKEN = "tu_token_de_acceso"

sincronizar_operaciones(API_URL, TOKEN)

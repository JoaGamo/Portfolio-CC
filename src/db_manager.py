import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import DictCursor
from typing import Dict, List, Any, Optional
from datetime import datetime
from functools import wraps

# Load environment variables from .env file
load_dotenv()

def singleton(cls):
    """Decorator para implementar el patrón Singleton"""
    instances = {}
    
    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance

@singleton
class DatabaseManager:
    def __init__(self):
        if hasattr(self, 'initialized'):
            return
            
        self.connection_params = {
            "dbname": os.getenv('POSTGRES_DB', 'bolsa_de_valores'),
            "user": os.getenv('POSTGRES_USER', 'postgres'),
            "password": os.getenv('POSTGRES_PASSWORD'),
            "host": os.getenv('POSTGRES_HOST', 'localhost'),
            "port": os.getenv('POSTGRES_PORT', '5432')
        }
        
        # Verify required environment variables
        if not self.connection_params["password"]:
            raise ValueError("POSTGRES_PASSWORD environment variable is required")
            
        self.conn = None
        self.cur = None
        self.initialized = True

    def conectar(self) -> None:
        """Establece la conexión a la base de datos"""
        try:
            self.conn = psycopg2.connect(**self.connection_params)
            self.cur = self.conn.cursor(cursor_factory=DictCursor)
        except psycopg2.Error as e:
            raise Exception(f"Error al conectar a la base de datos: {e}")

    def desconectar(self) -> None:
        """Cierra la conexión a la base de datos"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    def insertar_operacion(self, operacion: Dict[str, Any]) -> int:
        """Inserta una nueva operación y retorna su ID"""
        try:
            if not self.conn or self.conn.closed:
                self.conectar()
            
            campos = ", ".join(operacion.keys())
            placeholders = ", ".join(["%s"] * len(operacion))
            query = f"""
                INSERT INTO operacion ({campos})
                VALUES ({placeholders})
                RETURNING id;
            """
            
            self.cur.execute(query, tuple(operacion.values()))
            operation_id = self.cur.fetchone()[0]
            self.conn.commit()
            return operation_id
            
        except psycopg2.Error as e:
            self.conn.rollback()
            raise Exception(f"Error al insertar la operación: {e}")

    def obtener_operaciones(self, 
                        ticker: Optional[str] = None, 
                        fecha_inicio: Optional[datetime] = None,
                        fecha_fin: Optional[datetime] = None) -> List[Dict]:
        """Obtiene operaciones con filtros opcionales"""
        try:
            if not self.conn or self.conn.closed:
                self.conectar()

            conditions = []
            params = []

            if ticker:
                conditions.append("ticker = %s")
                params.append(ticker)
            if fecha_inicio:
                conditions.append("fecha >= %s")
                params.append(fecha_inicio)
            if fecha_fin:
                conditions.append("fecha <= %s")
                params.append(fecha_fin)

            query = "SELECT * FROM operacion"
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY fecha"
            
            self.cur.execute(query, params)
            return [dict(row) for row in self.cur.fetchall()]

        except psycopg2.Error as e:
            raise Exception(f"Error al obtener las operaciones: {e}")

    def __enter__(self):
        self.conectar()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.desconectar()

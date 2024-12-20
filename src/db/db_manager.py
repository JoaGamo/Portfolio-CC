import os
from dotenv import load_dotenv
import psycopg2
from utils.utils import obtener_dolar_ccl_con_fecha, obtener_dolar_ccl_con_fecha_compra
from psycopg2.extras import DictCursor
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from functools import wraps
from contextlib import contextmanager
from utils.utils import obtener_precio_actual

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
        
        if not self.connection_params["password"]:
            raise ValueError("POSTGRES_PASSWORD environment variable is required")
            
        self.initialized = True

    @contextmanager
    def get_cursor(self):
        """Context manager para obtener un cursor dedicado"""
        conn = psycopg2.connect(**self.connection_params)
        try:
            cursor = conn.cursor(cursor_factory=DictCursor)
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def insertar_operacion(self, operacion: Dict[str, Any]) -> int:
        """Inserta una nueva operación y retorna su ID"""
        try:
            campos = ", ".join(operacion.keys())
            placeholders = ", ".join(["%s"] * len(operacion))
            query = f"""
                INSERT INTO operacion ({campos})
                VALUES ({placeholders})
                RETURNING id;
            """
            
            with self.get_cursor() as cursor:
                cursor.execute(query, tuple(operacion.values()))
                operation_id = cursor.fetchone()[0]
                return operation_id
            
        except Exception as e:
            raise Exception(f"Error al insertar la operación: {e}")

    def obtener_operaciones(self, 
                        ticker: Optional[str] = None, 
                        fecha_inicio: Optional[datetime] = None,
                        fecha_fin: Optional[datetime] = None) -> List[Dict]:
        """Obtiene operaciones con filtros opcionales"""
        try:
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
            
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            raise Exception(f"Error al obtener las operaciones: {e}")
        
        
    def obtener_operaciones_unicas(self) -> List[Dict]:
        """Retorna un listado de tickers únicos históricamente operados"""
        try:
            query = """
                SELECT DISTINCT ticker 
                FROM operacion 
                ORDER BY ticker;
            """
            with self.get_cursor() as cursor:
                cursor.execute(query)
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            raise Exception(f"Error al obtener las operaciones únicas: {e}")

    def obtener_cantidad_actual(self, ticker) -> float:
        """Obtiene la cantidad actual de un ticker (compras - ventas)"""
        try:
            query = """
                SELECT tipo_operacion, cantidad 
                FROM operacion 
                WHERE ticker = %s
            """
            with self.get_cursor() as cursor:
                cursor.execute(query, (ticker,))
                cantidad_total = 0.0
                
                for row in cursor.fetchall():
                    if row['tipo_operacion'] == 'compra':
                        cantidad_total += float(row['cantidad'])
                    elif row['tipo_operacion'] == 'venta':
                        cantidad_total -= float(row['cantidad'])
                
                return cantidad_total
                
        except Exception as e:
            raise Exception(f"Error al obtener la cantidad de operaciones: {e}")
      

    def obtener_profit_actual(self, ticker) -> float:
        """Obtiene el profit actual de un ticker"""
        try:
            query = """
                SELECT 
                    tipo_operacion, 
                    cantidad, 
                    precio, 
                    moneda, 
                    fecha,
                    TO_CHAR(fecha, 'DD') as dia,
                    TO_CHAR(fecha, 'MM') as mes,
                    TO_CHAR(fecha, 'YYYY') as anio
                FROM operacion 
                WHERE ticker = %s
            """
            with self.get_cursor() as cursor:
                cursor.execute(query, (ticker,))
                profit_total = 0.0
                
                for row in cursor.fetchall():
                    dia = row["dia"]
                    mes = row["mes"]
                    anio = row["anio"]
                    
                    if row['tipo_operacion'] == 'compra':
                        if row['moneda'] == 'ARS':
                            profit_total -= float(row['cantidad']) * float(row['precio'])
                        else:
                            profit_total -= float(row['cantidad']) * float(row['precio']) * obtener_dolar_ccl_con_fecha(anio, mes, dia)
                    elif row['tipo_operacion'] == 'venta':
                        if row['moneda'] == 'ARS':
                            profit_total += float(row['cantidad']) * float(row['precio'])
                        else:
                            profit_total += float(row['cantidad']) * float(row['precio']) * obtener_dolar_ccl_con_fecha(anio, mes, dia)
                            
                
            cantidadActual = self.obtener_cantidad_actual(ticker)
            if cantidadActual > 0:
                profit_total += cantidadActual * obtener_precio_actual(ticker)
            
            return profit_total
            
        except psycopg2.Error as e:
            raise Exception(f"Error al obtener el profit de operaciones: {e}")
        
        
    def obtener_profit_actual_usd(self, ticker) -> float:
        """Obtiene el profit actual convertido a USD (dolar CCL) de un ticker"""
        try:
            query = """
                SELECT 
                    tipo_operacion, 
                    cantidad, 
                    precio, 
                    moneda, 
                    fecha,
                    TO_CHAR(fecha, 'DD') as dia,
                    TO_CHAR(fecha, 'MM') as mes,
                    TO_CHAR(fecha, 'YYYY') as anio
                FROM operacion 
                WHERE ticker = %s
            """
            with self.get_cursor() as cursor:
                cursor.execute(query, (ticker,))
                profit_total = 0.0
                
                for row in cursor.fetchall():
                    dia = row["dia"]
                    mes = row["mes"]
                    anio = row["anio"]
                    
                    if row['tipo_operacion'] == 'compra':
                        if row['moneda'] == 'USD':
                            profit_total -= float(row['cantidad']) * float(row['precio'])
                        else:
                            profit_total -= float(row['cantidad']) * float(row['precio']) / obtener_dolar_ccl_con_fecha_compra(anio, mes, dia)
                    elif row['tipo_operacion'] == 'venta':
                        if row['moneda'] == 'USD':
                            profit_total += float(row['cantidad']) * float(row['precio'])
                        else:
                            profit_total += float(row['cantidad']) * float(row['precio']) / obtener_dolar_ccl_con_fecha(anio, mes, dia)

            cantidadActual = self.obtener_cantidad_actual(ticker)
            
            if cantidadActual > 0:
                today = datetime.now() - timedelta(days=1)
                dia = today.strftime("%d")
                mes = today.strftime("%m")
                anio = today.strftime("%Y")
                profit_total += cantidadActual * obtener_precio_actual(ticker) / obtener_dolar_ccl_con_fecha_compra(anio, mes, dia)
            
            return profit_total
            
        except psycopg2.Error as e:
            raise Exception(f"Error al obtener el profit en USD de operaciones: {e}")

    def obtener_operacion_cache(self, numero: int) -> Optional[Dict]:
        """Obtiene una operación cacheada por su número"""
        try:
            query = """
                SELECT datos FROM operacion_iol_cache 
                WHERE numero = %s AND fecha_obtencion > NOW() - INTERVAL '1 day'
            """
            with self.get_cursor() as cursor:
                cursor.execute(query, (numero,))
                result = cursor.fetchone()
                return result[0] if result else None
            
        except Exception as e:
            raise Exception(f"Error al obtener la operación cacheada: {e}")

    def guardar_operacion_cache(self, numero: int, datos: Dict) -> None:
        """Guarda o actualiza una operación en la caché"""
        try:
            query = """
                INSERT INTO operacion_iol_cache (numero, datos)
                VALUES (%s, %s)
                ON CONFLICT (numero) DO UPDATE 
                SET datos = EXCLUDED.datos,
                    fecha_obtencion = CURRENT_TIMESTAMP
            """
            with self.get_cursor() as cursor:
                cursor.execute(query, (numero, psycopg2.extras.Json(datos)))
            
        except Exception as e:
            raise Exception(f"Error al guardar la operación en caché: {e}")

    def obtener_operaciones_conocidas(self) -> List[int]:
        """Obtiene lista de números de operaciones ya conocidas"""
        try:
            query = "SELECT numeros_conocidos FROM iol_sync_log ORDER BY ultima_sync DESC LIMIT 1"
            with self.get_cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                return result[0] if result else []
            
        except Exception as e:
            raise Exception(f"Error al obtener operaciones conocidas: {e}")

    def actualizar_operaciones_conocidas(self, numeros: List[int]) -> None:
        """Actualiza el registro de operaciones conocidas"""
        try:
            query = """
                INSERT INTO iol_sync_log (numeros_conocidos)
                VALUES (%s)
            """
            with self.get_cursor() as cursor:
                cursor.execute(query, (numeros,))
            
        except Exception as e:
            raise Exception(f"Error al actualizar operaciones conocidas: {e}")
        
    def obtener_color(self, ticker: str) -> str:
        """Obtiene el color de un ticker"""
        try:
            query = """
                SELECT color FROM colores_alterno WHERE ticker = %s
            """
            with self.get_cursor() as cursor:
                cursor.execute(query, (ticker,))
                result = cursor.fetchone()
                return result[0] if result else None # type: ignore
            
        except Exception as e:
            raise Exception(f"Error al obtener el color del ticker: {e}")

    def guardar_color(self, ticker: str, color: str) -> None:
        """Guarda o actualiza el color de un ticker"""
        try:
            query = """
                INSERT INTO colores_alterno (ticker, color)
                VALUES (%s, %s)
                ON CONFLICT (ticker) DO UPDATE 
                SET color = EXCLUDED.color
            """
            with self.get_cursor() as cursor:
                cursor.execute(query, (ticker, color))
        except Exception as e:
            raise Exception(f"Error al guardar el color del ticker: {e}")

    def obtener_colores_usados(self) -> List[str]:
        """Obtiene la lista de colores ya asignados a tickers activos"""
        try:
            query = """
                SELECT DISTINCT c.color
                FROM colores_alterno c
                JOIN operacion o ON c.ticker = o.ticker
                GROUP BY c.ticker, c.color
                HAVING SUM(CASE WHEN o.tipo_operacion = 'compra' THEN o.cantidad 
                              WHEN o.tipo_operacion = 'venta' THEN -o.cantidad 
                              ELSE 0 END) > 0
            """
            with self.get_cursor() as cursor:
                cursor.execute(query)
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            raise Exception(f"Error al obtener colores usados: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

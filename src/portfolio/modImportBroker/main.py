from dotenv import load_dotenv
import os
from CommonIOL import IOLClient
from db_manager import DatabaseManager

def create_client(client_type="IOL"):
    if client_type == "IOL":
        return IOLClient(
            usuario=os.getenv("IOL_USUARIO"),
            contrasena=os.getenv("IOL_CONTRASENA"),
            fecha_desde=os.getenv("IOL_FECHA_DESDE")
        )
    # if client_type == "PPI": Acá se puede ir agregando más...
    raise Exception("Broker no soportado")

def actualizar_portfolio(client):
    """Actualiza el portfolio en la base de datos"""
    db = DatabaseManager()
    operaciones = client.obtener_operaciones()
    
    for operacion in operaciones:
        operacion_db = {
            'fecha': client.obtener_fecha(operacion),
            'tipo_operacion': client.obtener_tipo(operacion).lower(),
            'tipo_instrumento': client.obtener_tipo_instrumento(operacion),
            'ticker': client.obtener_simbolo(operacion),
            'cantidad': client.obtener_cantidad(operacion),
            'precio': client.obtener_precio(operacion),
            'comisiones': client.obtener_comision(operacion),
            'mercado': client.obtener_mercado(operacion),
            'notas': f"Operación importada desde {client.__class__.__name__}"
        }
        try:
            with db:
                db.insertar_operacion(operacion_db)
        except Exception as e:
            print(f"Error al insertar operación {operacion_db['ticker']}: {str(e)}")

def main():
    load_dotenv()
    client = create_client()
    actualizar_portfolio(client)

if __name__ == "__main__":
    main()
from dotenv import load_dotenv
import os
from CommonIOL import IOLClient
from Getquin import GetquinClient

def create_client(client_type="IOL"):
    if client_type == "IOL":
        return IOLClient(
            usuario=os.getenv("IOL_USUARIO"),
            contrasena=os.getenv("IOL_CONTRASENA"),
            fecha_desde=os.getenv("IOL_FECHA_DESDE")
        )
    # if client_type == "PPI": Acá se puede ir agregando más...
    raise Exception("Broker no soportado")

def actualizar_portfolio(client, ghostfolio):
    operaciones = client.obtener_operaciones()
    for operacion in operaciones:
        simbolo = client.obtener_simbolo(operacion)
        cantidad = client.obtener_cantidad(operacion)
        precio = client.obtener_precio(operacion)
        fecha = client.obtener_fecha(operacion)
        tipo = client.obtener_tipo(operacion)
        moneda = client.obtener_moneda(operacion)
        mercado = client.obtener_mercado(operacion)
        ghostfolio.insertar_operacion(simbolo, cantidad, precio, fecha, tipo, moneda, mercado)

    fallas = ghostfolio.obtener_operaciones_fallidas()
    if fallas:
        print("Operaciones fallidas:")
        for falla in fallas:
            print("------------------")
            print(f"Símbolo: {falla['symbol']}, Fecha: {falla['date']}")
            print(f"Error: {falla['error']}\n")
    
def main():
    load_dotenv()
    client = create_client()
    ghostfolio = GetquinClient()
    actualizar_portfolio(client, ghostfolio)

if __name__ == "__main__":
    main()
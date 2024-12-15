import requests

def obtener_dolar_ccl_con_fecha(dia, mes, anio):
    req = requests.get(f"https://api.argentinadatos.com/v1/cotizaciones/dolares/contadoconliqui/{anio}/{mes}/{dia}")
    if req.status_code != 200:
        raise Exception(f"Error al obtener la cotización del dólar CCL: {req.text}")
    return req.json()['venta']

def obtener_portfolio_piechart() -> str:
    """Retorna el archivo"""
    return "test"
    
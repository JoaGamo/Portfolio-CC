from typing import Any, Dict, List
from datetime import datetime
import requests
import pytz
from CommonBroker import CommonBroker
from db_manager import DatabaseManager

class IOLClient(CommonBroker):
    def __init__(self, **kwargs):
        self.usuario = kwargs.get('usuario')
        self.contrasena = kwargs.get('contrasena')
        self.fecha_desde = kwargs.get('fecha_desde')
        self.access_token = None
        self.refresh_token = None
        
        
    def _inicializar_tokens(self):
        url = "https://api.invertironline.com/token"
        payload = {
            "grant_type": "password",
            "username": self.usuario,
            "password": self.contrasena,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
        tokens = response.json()
        self.access_token = tokens["access_token"]
        self.refresh_token = tokens["refresh_token"]


    def _renovar_tokens(self):
        url = "https://api.invertironline.com/token"
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
        tokens = response.json()
        self.access_token = tokens["access_token"]
        self.refresh_token = tokens["refresh_token"]


    def _asegurar_token_valido(self): # type: ignore
        if not self.access_token:
            self._inicializar_tokens()
        try:
            return self.access_token
        except requests.exceptions.HTTPError:
            self._renovar_tokens()
            return self.access_token


    def obtener_operaciones(self):
        token = self._asegurar_token_valido()
        url = "https://api.invertironline.com/api/v2/operaciones"
        payload = {
            "filtro.fechaDesde": self.fecha_desde,
            "filtro.estado": "terminadas"
        }
        headers = {"Authorization": f"Bearer {token}"}
        
        db = DatabaseManager()
        operaciones_conocidas = db.obtener_operaciones_conocidas()
        
        response = requests.get(url, params=payload, headers=headers)
        response.raise_for_status()
        aConvertir = response.json()

        numeros = []
        dividendos = []
        operaciones = []
        nuevos_numeros = set()

        for operacion in aConvertir:
            try:
                if operacion["tipo"] == "Pago de Dividendos":
                    dividendos.append(operacion)
                else:
                    numero = operacion["numero"]
                    nuevos_numeros.add(numero)
                    if numero not in operaciones_conocidas:
                        numeros.append(numero)
            except TypeError as e:
                mensaje = """
                    Error al procesar operación de IOL.
                    Si son las 12 de la noche, IOL apagó sus servidores 👍
                    
                    Respuesta de la API:
                    {}
                    
                    PD: Si no es de noche, algo salió mal en serio.
                    Error original: {}
                """.format(response.text, str(e))
                raise TypeError(mensaje)

        # Actualizar lista de operaciones conocidas
        with db:
            db.actualizar_operaciones_conocidas(list(nuevos_numeros))

        # Solo obtener detalles de operaciones nuevas
        for numero in numeros:
            operaciones.append(self.obtener_operacion_completa(numero).json()) # type: ignore
        
        # TODO: Implementar manejo de dividendos en IOL
        if dividendos:
            manejador_dividendos = self.IOL_manejador_dividendos(dividendos)
            print("TODO: Implementar manejo de dividendos en IOL")
            print("Dividendos capturados sin procesar:")
            print(dividendos)
            # operaciones.extend(dividendos)
        
        return operaciones
        
        
    
    # En IOL debemos hacer una segunda API Call por cada operación para obtener la operación completa
    # Junto con su tipo de moneda y todo lo demás :D
    # TODO: Caching de API calls de IOL
    def obtener_operacion_completa(self, numero):
        # Intentar obtener de la caché primero
        db = DatabaseManager()
        with db:
            cached = db.obtener_operacion_cache(numero)
            if cached:
                return type('Response', (), {'json': lambda: cached})()

        # Si no está en caché, obtener de la API
        token = self._asegurar_token_valido()
        url = f"https://api.invertironline.com/api/v2/operaciones/{numero}"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        with db:
            db.guardar_operacion_cache(numero, response.json())

        return response

    def obtener_simbolo(self, operacion: Dict[str, Any]) -> str:
        return operacion["simbolo"].split()[0]

    def obtener_cantidad(self, operacion: Dict[str, Any]) -> int:
        if operacion.get("operaciones"):
            return operacion["operaciones"][0]["cantidad"]
        return operacion.get("cantidad", 0)

    def obtener_precio(self, operacion: Dict[str, Any]) -> float:
        if operacion.get("operaciones"):
            
            return float(operacion["operaciones"][0]["precio"])
        return float(operacion.get("precio", 0))


    def obtener_fecha(self, operacion: Dict[str, Any]) -> str:
        """Obtiene la fecha y la convierte de Argentina (UTC-3) a UTC"""
        fecha_str = operacion.get("fechaOperado", "")
        
        argentina_tz = pytz.timezone('America/Argentina/Buenos_Aires')
        fecha_arg = argentina_tz.localize(datetime.fromisoformat(fecha_str))
        
        fecha_utc = fecha_arg.astimezone(pytz.UTC)
        
        # Format as required "YYYY-MM-DDT05:00:00.000Z"
        return fecha_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')


    def obtener_tipo(self, operacion: Dict[str, Any]) -> str:
        """Obtiene el tipo de operación según el schema de la base de datos"""
        tipo_map = {
            "compra": "compra",
            "suscripcionfci": "compra",
            "venta": "venta", 
            "rescatefci": "venta",
            "pago_dividendos": "dividendo"
        }
        return tipo_map.get(operacion["tipo"].lower(), "desconocido")
    
    def obtener_tipo_instrumento(self, operacion):
        # En IOL no se especifica el tipo de instrumento, por lo que asumiremos que todos son acciones
        return "accion"


    def obtener_moneda(self, operacion: Dict[str, Any]) -> str:
        return "ARS" if operacion["moneda"].lower() == "peso_argentino" else "USD"
        

    def obtener_mercado(self, operacion: Dict[str, Any]) -> str:
        return "BCBA" if operacion["mercado"].lower() == "bcba" else "NASDAQ"
    
    def obtener_comision(self, operacion: Dict[str, Any]) -> float:
        moneda = self.obtener_moneda(operacion)
        if moneda == "USD":
            return operacion['arancelesUSD']
        else:
            return operacion['arancelesARS']

        
    class IOL_manejador_dividendos(CommonBroker):
        def __init__(self, dividendos):
            self.dividendos = dividendos

        def _inicializar_tokens(self):
            raise NotImplementedError


        def _renovar_tokens(self):
            raise NotImplementedError


        def _asegurar_token_valido(self):
            raise NotImplementedError

        def obtener_simbolo(self, operacion: Dict[str, Any]) -> str:
            return operacion["simbolo"].split()[0]

        def obtener_cantidad(self, operacion: Dict[str, Any]) -> int:
            return operacion.get("cantidad", 0)

        def obtener_precio(self, operacion: Dict[str, Any]) -> float:
            return float(operacion.get("precio", 0))
        
        def obtener_fecha(self, operacion: Dict[str, Any]) -> str:
            """Obtiene la fecha y la retorna como YYYY-MM-DD"""
            fecha = operacion.get("fechaOperada", "")
            return fecha
        
        def obtener_tipo(self, operacion: Dict[str, Any]) -> str:
            return "DIVIDEND"
        
        def obtener_moneda(self, operacion: Dict[str, Any]) -> str:
            return "ARS" if operacion["moneda"].lower() == "peso_argentino" else "USD"
        
        def obtener_mercado(self, operacion: Dict[str, Any]) -> str:
            return "ARG" if operacion["mercado"].lower() == "bcba" else "USA"
        
        def obtener_comision(self, operacion: Dict[str, Any]) -> float:
            return 0
        
        def obtener_operaciones(self) -> List[Dict[str, Any]]:
            raise NotImplementedError

        def obtener_tipo_instrumento(self, operacion: Dict[str, Any]) -> str:
            raise NotImplementedError





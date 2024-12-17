import requests
import subprocess
import os
import tempfile
from base64 import b64decode
import yfinance as yf


def obtener_dolar_ccl_con_fecha(dia, mes, anio):
    req = requests.get(f"https://api.argentinadatos.com/v1/cotizaciones/dolares/contadoconliqui/{anio}/{mes}/{dia}")
    if req.status_code != 200:
        raise Exception(f"Error al obtener la cotización del dólar CCL: {req.text}")
    return req.json()['venta']


def process_chart_with_sanjuuni(image_data: bytes) -> bytes:
    """Process image data with sanjuuni and return the .bimg content"""
    
    print("Iniciando procesamiento con sanjuuni")
    
    # Crear directorio de debug si no existe
    debug_dir = "debug_images"
    if not os.path.exists(debug_dir):
        os.makedirs(debug_dir)
    
    # Guardar una copia de la imagen de entrada para debug
    debug_input_path = os.path.join(debug_dir, "last_input.png")
    debug_output_path = os.path.join(debug_dir, "last_output.bimg")
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, "chart.png")
        output_path = os.path.join(temp_dir, "chart.bimg")
        
        try:
            # Guardar la imagen en el directorio temporal
            with open(input_path, "wb") as f:
                f.write(image_data)
            
            # Guardar una copia para debug
            with open(debug_input_path, "wb") as f:
                f.write(image_data)
            
            print(f"Imagen de entrada guardada en: {debug_input_path}")
            
            # Procesar con sanjuuni
            subprocess.run([
                "sanjuuni",
                "-i", input_path,
                "--disable-opencl",
                "-p",
                "-k",
                "--blit-image",
                "-o", output_path,
                "width=1000",
                "height=1000"
            ], check=True)
            
            # Leer y retornar el archivo procesado correctamente
            with open(output_path, "rb") as f:
                bimg_data = f.read()
            
            with open(debug_output_path, "wb") as f:
                f.write(bimg_data)
            
            return bimg_data
                
        except Exception as e:
            raise Exception(f"Error processing image with sanjuuni: {e}")


def obtener_precio_actual(ticker: str) -> float:
    """
    Obtiene el precio actual de un ticker usando Yahoo Finance.
    """
    try:
        # Ajustar ticker para acciones argentinas
        
        ticker = f"{ticker}.BA"
            
        stock = yf.Ticker(ticker)
        current_price = stock.info['regularMarketPreviousClose']
        return float(current_price)
    except Exception as e:
        #print(f"Error obteniendo precio para {ticker}: {e}")
        #print("No todos los CEDEARs están en Yahoo... :/")
        return 0.0
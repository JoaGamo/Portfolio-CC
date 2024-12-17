import os
import requests
import json
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional, List, Dict
from db.db_manager import DatabaseManager
from fastapi.responses import Response
from utils.utils import obtener_precio_actual, process_chart_with_sanjuuni
import base64

# Load environment variables
load_dotenv()
QUICKCHART_API_URL = os.getenv('QUICKCHART_API_URL', 'http://quickchart:3400')

app = FastAPI(
    title="Portfolio API",
    description="API para consultar operaciones del portfolio",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/operaciones/", response_model=List[Dict])
async def obtener_operaciones_all(
    fecha_inicio: Optional[datetime] = Query(None, description="Fecha inicial (YYYY-MM-DD)"),
    fecha_fin: Optional[datetime] = Query(None, description="Fecha final (YYYY-MM-DD)")
):
    """
    Obtiene lista de todas las operaciones
    """
    try:
        with DatabaseManager() as db:
            operaciones = db.obtener_operaciones(
                ticker=None,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )
            return operaciones
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tickers_unicos", response_model=List[str])
async def obtener_tickers_unicos():
    """
    Obtiene lista de tickers históricos únicos
    """
    try:
        with DatabaseManager() as db:
            tickers = db.obtener_operaciones_unicas()
            return [ticker['ticker'] for ticker in tickers]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/operaciones/{ticker}", response_model=List[Dict])
async def obtener_operaciones_ticker(
    ticker: str,
    fecha_inicio: Optional[datetime] = Query(None, description="Fecha inicial (YYYY-MM-DD)"),
    fecha_fin: Optional[datetime] = Query(None, description="Fecha final (YYYY-MM-DD)")
):
    """
    Obtiene lista de operaciones por ticker específico
    """
    try:
        with DatabaseManager() as db:
            operaciones = db.obtener_operaciones(
                ticker=ticker,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )
            return operaciones
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/profit_actual/{ticker}", response_model=float)
async def obtener_profit_actual(ticker: str):
    """
    Obtiene el profit actual de un ticker
    """
    try:
        with DatabaseManager() as db:
            profit_actual = db.obtener_profit_actual(ticker)
            return profit_actual
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
@app.get("/cantidad_actual/", response_model=float)
async def obtener_cantidad_actual(ticker: str):
    """
    Obtiene la cantidad actual de un ticker (compras - ventas)
    """
    try:
        with DatabaseManager() as db:
            cantidad_actual = db.obtener_cantidad_actual(ticker)
            return cantidad_actual
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def asignar_colores_portfolio(db: DatabaseManager, portfolio: List[Dict]) -> Dict[str, str]:
    """Asigna colores a los tickers del portfolio que no tengan uno asignado"""
    # Obtener colores ya asignados
    colores_asignados = {}
    for item in portfolio:
        ticker = item['ticker']
        color = db.obtener_color(ticker)
        if color:
            colores_asignados[ticker] = color
    
    # Asignar colores a tickers sin color
    colores_usados = db.obtener_colores_usados()
    colores_disponibles = [c for c in AVAILABLE_COLORS if c not in colores_usados]
    
    for item in portfolio:
        ticker = item['ticker']
        if ticker not in colores_asignados:
            if not colores_disponibles:
                colores_disponibles = AVAILABLE_COLORS.copy()
            
            nuevo_color = colores_disponibles.pop(0)
            db.guardar_color(ticker, nuevo_color)
            colores_asignados[ticker] = nuevo_color
    
    return colores_asignados

@app.get("/portfolio", response_model=List[Dict])
async def obtener_portfolio():
    """Obtiene el portfolio actual (listado de tickers con cantidad > 0)"""
    try:
        with DatabaseManager() as db:
            operaciones = db.obtener_operaciones()
            portfolio = {}
            
            for operacion in operaciones:
                ticker = operacion['ticker']
                cantidad = db.obtener_cantidad_actual(ticker)
                if cantidad > 0:
                    if ticker not in portfolio:
                        portfolio[ticker] = {
                            "ticker": ticker,
                            "cantidad": cantidad
                        }
            
            portfolio_list = list(portfolio.values())
            # Asignar colores al portfolio
            colores = await asignar_colores_portfolio(db, portfolio_list)
            
            # Agregar color a cada item del portfolio
            porcentajes = await calcular_porcentaje_portfolio(portfolio_list)
            
            for item in portfolio_list:
                item['color'] = colores.get(item['ticker'])
                item['porcentaje'] = next(p['porcentaje'] for p in porcentajes if p['ticker'] == item['ticker'])
                
            return portfolio_list
            
    except Exception as e:
        print("error en portfolio: ", e)
        raise HTTPException(status_code=500, detail=str(e))
    
    
async def calcular_porcentaje_portfolio(holdings: list) -> list:
    """
    Calcula el porcentaje de cada holding en el portfolio
    """
    total_value = 0
    for holding in holdings:
        precio = obtener_precio_actual(holding['ticker'])
        holding['valor'] = precio * holding['cantidad']
        total_value += holding['valor']

    for holding in holdings:
        holding['porcentaje'] = (holding['valor'] / total_value) * 100 if total_value > 0 else 0
        
    return holdings
    
    
AVAILABLE_COLORS = [
    'orange', 'blue', 'yellow', 'red', 'green', 'purple', 'magenta', 'lime', 'cyan'
]

@app.get("/portfolio/colores", response_model=Dict[str, str])
async def obtener_colores():
    """Obtiene y asigna los colores de los tickers del portfolio"""
    try:
        with DatabaseManager() as db:
            portfolio = await obtener_portfolio()
            return await asignar_colores_portfolio(db, portfolio)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def generate_portfolio_chart(portfolio_data: List[Dict], colors_data: Dict[str, str]) -> str:
    """Generate a pie chart configuration string for the portfolio"""
    labels = []
    values = []
    colors = []
    
    for item in portfolio_data:
        ticker = item['ticker']
        labels.append(ticker)
        values.append(float(item['porcentaje']))
        colors.append(colors_data.get(ticker, 'gray'))
    
    chart_config = {
        "type": "pie",
        "data": {
            "labels": labels,
            "datasets": [{
                "data": values,
                "backgroundColor": colors
            }]
        },
        "options": {
            "tooltips": {"enabled": False},
            "plugins": {"datalabels": {"display": False}},
            "legend": {"display": False},
            "devicePixelRatio": 2
        }
    }
    
    return json.dumps(chart_config)

@app.get("/portfolio/chart")
async def obtener_portfolio_chart():
    try:
        portfolio = await obtener_portfolio()
        colores = await obtener_colores()
        
        chart_config = await generate_portfolio_chart(portfolio, colores)
        
        print(f"{QUICKCHART_API_URL}/chart?w=1000&h=1000&c={chart_config}")
        
        response = requests.get(
            f"{QUICKCHART_API_URL}/chart",
            params={
                "w": 1000,
                "h": 1000,
                "c": chart_config
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Error al generar el chart")

        # Procesar la imagen y obtener la tabla bimg sin codificar a base64
        bimg_data = process_chart_with_sanjuuni(response.content)
        
        # Devolver los datos binarios directamente
        return Response(
            content=bimg_data,
            media_type="application/octet-stream",
            headers={"Content-Disposition": "attachment; filename=portfolio.bimg"}
        )
            
    except Exception as e:
        print("Error en el chart: ", e)
        raise HTTPException(status_code=500, detail=f"Error generando el chart: {str(e)}")


@app.get("/portfolio/color/{ticker}")
async def obtener_color_ticker(ticker: str):
    """
    Obtiene el color de un ticker
    """
    try:
        with DatabaseManager() as db:
            color = db.obtener_color(ticker)
            return color
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Endpoint de verificación de API"""
    return {"status": "ok", "message": "Portfolio API running"}

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional, List, Dict
from db.db_manager import DatabaseManager

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
        db = DatabaseManager()
        with db:
            operaciones = db.obtener_operaciones(
                ticker=None,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )
            return operaciones
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
        db = DatabaseManager()
        with db:
            operaciones = db.obtener_operaciones(
                ticker=ticker,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )
            return operaciones
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.get("/cantidad_actual/", response_model=float)
async def obtener_cantidad_actual(ticker: str):
    """
    Obtiene la cantidad actual de un ticker (compras - ventas)
    """
    try:
        db = DatabaseManager()
        with db:
            cantidad_actual = db.obtener_cantidad_actual(ticker)
            return cantidad_actual
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/")
async def root():
    """Endpoint de verificación de API"""
    return {"status": "ok", "message": "Portfolio API running"}


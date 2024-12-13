from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional, List, Dict
from db_manager import DatabaseManager

app = FastAPI(
    title="Portfolio API",
    description="API para consultar operaciones del portfolio",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/operaciones/", response_model=List[Dict])
async def obtener_operaciones(
    ticker: Optional[str] = Query(None, description="Filtrar por ticker"),
    fecha_inicio: Optional[datetime] = Query(None, description="Fecha inicial (YYYY-MM-DD)"),
    fecha_fin: Optional[datetime] = Query(None, description="Fecha final (YYYY-MM-DD)")
):
    """
    Obtiene lista de operaciones con filtros opcionales
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

@app.get("/")
async def root():
    """Endpoint de verificación de API"""
    return {"status": "ok", "message": "Portfolio API running"}

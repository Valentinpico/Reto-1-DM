from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import logging

from config.database import connect_to_mongo, close_mongo_connection
from routes.user_routes import router as user_router
from utils.middleware import setup_exception_handlers

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionar el ciclo de vida de la aplicación"""
    # Startup
    await connect_to_mongo()
    logger.info("🚀 Aplicación iniciada")
    yield
    # Shutdown
    await close_mongo_connection()
    logger.info("👋 Aplicación finalizada")


app = FastAPI(
    title="User Service API",
    description="Microservicio CRUD de usuarios con FastAPI y MongoDB",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar manejadores de excepciones
setup_exception_handlers(app)


# Middleware para medir tiempo de respuesta
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Middleware que mide el tiempo de respuesta de cada request
    y lo registra en los logs
    """
    start_time = time.time()
    
    # Log del request
    logger.info(f"📥 {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        
        # Agregar header con tiempo de respuesta
        response.headers["X-Process-Time-Ms"] = str(round(process_time, 2))
        
        # Log del response
        logger.info(
            f"📤 {request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {round(process_time, 2)}ms"
        )
        
        return response
    except Exception as e:
        process_time = (time.time() - start_time) * 1000
        logger.error(
            f"❌ {request.method} {request.url.path} - "
            f"Error: {str(e)} - "
            f"Time: {round(process_time, 2)}ms"
        )
        raise


# Los manejadores de excepciones ya están configurados en setup_exception_handlers


# Incluir routers
app.include_router(user_router)

# Importar respuestas estandarizadas
from utils.response import success_response
from models.responses import HealthResponseModel


# Endpoint de salud
@app.get(
    "/",
    tags=["health"],
    response_model=HealthResponseModel,
    summary="Health Check Básico",
    description="Verifica que la API esté funcionando correctamente"
)
async def health_check():
    """
    Health Check Básico
    
    Retorna información básica del servicio:
    - **service**: Nombre del servicio
    - **version**: Versión actual de la API
    """
    return success_response(
        data={
            "service": "User Service API",
            "version": "1.0.0"
        },
        message="API funcionando correctamente"
    )


@app.get(
    "/health",
    tags=["health"],
    response_model=HealthResponseModel,
    summary="Health Check Detallado",
    description="Verifica el estado del sistema incluyendo conexión a base de datos"
)
async def health():
    """
    Health Check Detallado
    
    Retorna el estado completo del sistema:
    - **database**: Estado de la conexión a MongoDB
    """
    return success_response(
        data={
            "database": "connected"
        },
        message="Sistema saludable"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

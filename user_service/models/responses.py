from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from models.user import UserResponse


class StandardResponseBase(BaseModel):
    """Modelo base de respuesta estandarizado"""
    success: bool = Field(..., description="Indica si la operación fue exitosa")
    statusCode: int = Field(..., description="Código de estado HTTP")
    message: str = Field(..., description="Mensaje descriptivo de la operación")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "statusCode": 200,
                "message": "Operación exitosa"
            }
        }


class UserResponseModel(StandardResponseBase):
    """Respuesta con un solo usuario"""
    data: Dict[str, Any] = Field(..., description="Datos del usuario")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "statusCode": 200,
                "message": "Usuario obtenido exitosamente",
                "data": {
                    "_id": "68eeafce05740b9d36aab307",
                    "name": "Juan Pérez",
                    "email": "juan@email.com"
                }
            }
        }


class UserListResponseModel(StandardResponseBase):
    """Respuesta con lista de usuarios"""
    data: List[Dict[str, Any]] = Field(..., description="Lista de usuarios")
    count: int = Field(..., description="Número total de usuarios")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "statusCode": 200,
                "message": "Se encontraron 2 usuarios",
                "data": [
                    {
                        "_id": "68eeafce05740b9d36aab307",
                        "name": "Juan Pérez",
                        "email": "juan@email.com"
                    },
                    {
                        "_id": "68eeafce05740b9d36aab308",
                        "name": "María García",
                        "email": "maria@email.com"
                    }
                ],
                "count": 2
            }
        }


class UserCreateResponseModel(StandardResponseBase):
    """Respuesta al crear un usuario"""
    data: Dict[str, Any] = Field(..., description="Datos del usuario creado")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "statusCode": 201,
                "message": "Usuario creado exitosamente",
                "data": {
                    "_id": "68eeafce05740b9d36aab307",
                    "name": "Juan Pérez",
                    "email": "juan@email.com"
                }
            }
        }


class UserDeleteResponseModel(StandardResponseBase):
    """Respuesta al eliminar un usuario"""
    data: Dict[str, int] = Field(..., description="Conteo de usuarios eliminados")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "statusCode": 200,
                "message": "Usuario eliminado exitosamente",
                "data": {
                    "deleted_count": 1
                }
            }
        }


class ErrorResponseModel(StandardResponseBase):
    """Respuesta de error estandarizada"""
    success: bool = Field(default=False, description="Siempre False en errores")
    data: Optional[Dict[str, Any]] = Field(None, description="Información adicional del error")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "statusCode": 404,
                "message": "Usuario no encontrado con identificador: 123abc",
                "data": {
                    "resource": "Usuario",
                    "identifier": "123abc"
                }
            }
        }


class HealthResponseModel(StandardResponseBase):
    """Respuesta del health check"""
    data: Dict[str, str] = Field(..., description="Estado del sistema")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "statusCode": 200,
                "message": "Sistema saludable",
                "data": {
                    "database": "connected"
                }
            }
        }

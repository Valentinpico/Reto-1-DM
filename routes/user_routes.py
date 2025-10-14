from fastapi import APIRouter, status
from typing import List, Dict, Any
import bcrypt
from bson import ObjectId

from models.user import UserCreate, UserUpdate, UserResponse
from models.responses import (
    UserResponseModel,
    UserListResponseModel,
    UserCreateResponseModel,
    UserDeleteResponseModel,
    ErrorResponseModel
)
from config.database import get_database
from utils.exceptions import (
    NotFoundException,
    AlreadyExistsException,
    BadRequestException
)
from utils.response import success_response

router = APIRouter(prefix="/api/users", tags=["users"])


def hash_password(password: str) -> str:
    """Encriptar password con bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


@router.get(
    "/",
    response_model=UserListResponseModel,
    responses={
        200: {
            "description": "Lista de usuarios obtenida exitosamente",
            "model": UserListResponseModel
        }
    }
)
async def get_all_users() -> Dict[str, Any]:
    """
    Obtener todos los usuarios
    
    Retorna una lista completa de todos los usuarios registrados en el sistema.
    - **Sin contraseñas**: Los passwords están excluidos de la respuesta
    - **Count**: Incluye el número total de usuarios encontrados
    """
    db = get_database()
    
    # Obtener todos los usuarios
    users_cursor = db.users.find({})
    users = await users_cursor.to_list(length=None)
    
    # Convertir ObjectId a string
    for user in users:
        user["_id"] = str(user["_id"])
    
    return success_response(
        data=users,
        message=f"Se encontraron {len(users)} usuarios"
    )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserCreateResponseModel,
    responses={
        201: {
            "description": "Usuario creado exitosamente",
            "model": UserCreateResponseModel
        },
        409: {
            "description": "El email ya está registrado",
            "model": ErrorResponseModel
        },
        422: {
            "description": "Errores de validación",
            "model": ErrorResponseModel
        }
    }
)
async def create_user(user: UserCreate) -> Dict[str, Any]:
    """
    Crear un nuevo usuario
    
    Crea un nuevo usuario en el sistema con los siguientes pasos:
    - **Encriptación**: La contraseña se encripta con bcrypt antes de guardar
    - **Validación de email único**: Verifica que el email no esté registrado
    - **Validaciones automáticas**: 
        - Email válido
        - Contraseña mínimo 6 caracteres
        - Nombre requerido
    """
    db = get_database()
    
    # Verificar si el email ya existe
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise AlreadyExistsException(
            resource="Usuario",
            identifier=f"email {user.email}"
        )
    
    # Preparar usuario con password encriptado
    user_dict = user.model_dump()
    user_dict["hashed_password"] = hash_password(user_dict.pop("password"))
    
    # Insertar en la base de datos
    result = await db.users.insert_one(user_dict)
    
    # Obtener usuario creado
    created_user = await db.users.find_one({"_id": result.inserted_id})
    created_user["_id"] = str(created_user["_id"])
    
    return success_response(
        data=created_user,
        message="Usuario creado exitosamente",
        status_code=status.HTTP_201_CREATED
    )


@router.get(
    "/{user_id}",
    response_model=UserResponseModel,
    responses={
        200: {
            "description": "Usuario obtenido exitosamente",
            "model": UserResponseModel
        },
        400: {
            "description": "ID de usuario inválido",
            "model": ErrorResponseModel
        },
        404: {
            "description": "Usuario no encontrado",
            "model": ErrorResponseModel
        }
    }
)
async def get_user(user_id: str) -> Dict[str, Any]:
    """
    Obtener un usuario por ID
    
    Busca y retorna un usuario específico por su identificador único.
    - **ID MongoDB**: Debe ser un ObjectId válido de MongoDB (24 caracteres hexadecimales)
    - **Sin password**: El password está excluido de la respuesta
    - **Error 404**: Si el usuario no existe
    """
    db = get_database()
    
    # Validar ObjectId
    if not ObjectId.is_valid(user_id):
        raise BadRequestException(
            message="ID de usuario inválido",
            identifier=user_id
        )
    
    # Buscar usuario
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    
    if not user:
        raise NotFoundException(
            resource="Usuario",
            identifier=user_id
        )
    
    user["_id"] = str(user["_id"])
    return success_response(
        data=user,
        message="Usuario obtenido exitosamente"
    )


@router.put(
    "/{user_id}",
    response_model=UserResponseModel,
    responses={
        200: {
            "description": "Usuario actualizado exitosamente",
            "model": UserResponseModel
        },
        400: {
            "description": "ID de usuario inválido",
            "model": ErrorResponseModel
        },
        404: {
            "description": "Usuario no encontrado",
            "model": ErrorResponseModel
        },
        409: {
            "description": "El email ya está registrado por otro usuario",
            "model": ErrorResponseModel
        },
        422: {
            "description": "Errores de validación",
            "model": ErrorResponseModel
        }
    }
)
async def update_user(user_id: str, user_update: UserUpdate) -> Dict[str, Any]:
    """
    Actualizar un usuario completo
    
    Actualiza todos los campos de un usuario existente.
    - **Validación previa**: Verifica que el usuario exista
    - **Email único**: Valida que el nuevo email no esté en uso por otro usuario
    - **Actualiza todos los campos**: name, email y password
    - **Re-encriptación**: Si se actualiza el password, se encripta nuevamente
    """
    db = get_database()
    
    # Validar ObjectId
    if not ObjectId.is_valid(user_id):
        raise BadRequestException(
            message="ID de usuario inválido",
            identifier=user_id
        )
    
    # Verificar que el usuario existe
    existing_user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not existing_user:
        raise NotFoundException(
            resource="Usuario",
            identifier=user_id
        )
    
    # Verificar si el email ya está en uso por otro usuario
    email_exists = await db.users.find_one({
        "email": user_update.email,
        "_id": {"$ne": ObjectId(user_id)}
    })
    if email_exists:
        raise AlreadyExistsException(
            resource="Usuario",
            identifier=f"email {user_update.email}"
        )
    
    # Preparar datos actualizados
    update_dict = user_update.model_dump()
    update_dict["hashed_password"] = hash_password(update_dict.pop("password"))
    
    # Actualizar usuario
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_dict}
    )
    
    # Obtener usuario actualizado
    updated_user = await db.users.find_one({"_id": ObjectId(user_id)})
    updated_user["_id"] = str(updated_user["_id"])
    
    return success_response(
        data=updated_user,
        message="Usuario actualizado exitosamente"
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserDeleteResponseModel,
    responses={
        200: {
            "description": "Usuario eliminado exitosamente",
            "model": UserDeleteResponseModel
        },
        400: {
            "description": "ID de usuario inválido",
            "model": ErrorResponseModel
        },
        404: {
            "description": "Usuario no encontrado",
            "model": ErrorResponseModel
        }
    }
)
async def delete_user(user_id: str) -> Dict[str, Any]:
    """
    Eliminar un usuario
    
    Elimina permanentemente un usuario del sistema.
    - **Verificación previa**: Confirma que el usuario existe antes de eliminar
    - **Eliminación permanente**: No se puede deshacer
    - **Confirmación**: Retorna el número de usuarios eliminados (deleted_count)
    """
    db = get_database()
    
    # Validar ObjectId
    if not ObjectId.is_valid(user_id):
        raise BadRequestException(
            message="ID de usuario inválido",
            identifier=user_id
        )
    
    # Verificar que el usuario existe
    existing_user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not existing_user:
        raise NotFoundException(
            resource="Usuario",
            identifier=user_id
        )
    
    # Eliminar usuario
    result = await db.users.delete_one({"_id": ObjectId(user_id)})
    
    return success_response(
        data={"deleted_count": result.deleted_count},
        message="Usuario eliminado exitosamente"
    )

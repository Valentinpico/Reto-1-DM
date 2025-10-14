from fastapi import HTTPException, status


class CustomHTTPException(HTTPException):
    """Excepción HTTP personalizada base"""
    def __init__(self, status_code: int, message: str, resource: str = None, identifier: str = None):
        self.message = message
        self.resource = resource
        self.identifier = identifier
        detail = self._build_detail()
        super().__init__(status_code=status_code, detail=detail)
    
    def _build_detail(self):
        """Construir el detalle del error"""
        detail = {"message": self.message}
        if self.resource:
            detail["resource"] = self.resource
        if self.identifier:
            detail["identifier"] = self.identifier
        return detail


class NotFoundException(CustomHTTPException):
    """Excepción para recursos no encontrados (404)"""
    def __init__(self, resource: str, identifier: str = None):
        message = f"{resource} no encontrado"
        if identifier:
            message += f" con identificador: {identifier}"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=message,
            resource=resource,
            identifier=identifier
        )


class AlreadyExistsException(CustomHTTPException):
    """Excepción para recursos que ya existen (409)"""
    def __init__(self, resource: str, identifier: str = None):
        message = f"{resource} ya existe"
        if identifier:
            message += f" con: {identifier}"
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=message,
            resource=resource,
            identifier=identifier
        )


class BadRequestException(CustomHTTPException):
    """Excepción para peticiones inválidas (400)"""
    def __init__(self, message: str, resource: str = None, identifier: str = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=message,
            resource=resource,
            identifier=identifier
        )


class UnauthorizedException(CustomHTTPException):
    """Excepción para acceso no autorizado (401)"""
    def __init__(self, message: str = "No autorizado"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message
        )


class ForbiddenException(CustomHTTPException):
    """Excepción para acceso prohibido (403)"""
    def __init__(self, message: str = "Acceso prohibido"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message=message
        )


class ValidationException(CustomHTTPException):
    """Excepción para errores de validación (422)"""
    def __init__(self, message: str, resource: str = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=message,
            resource=resource
        )


class InternalServerException(CustomHTTPException):
    """Excepción para errores internos del servidor (500)"""
    def __init__(self, message: str = "Error interno del servidor"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=message
        )

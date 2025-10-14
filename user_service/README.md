# 🚀 API de Usuarios - FastAPI + MongoDB

Un CRUD simple de usuarios con FastAPI y MongoDB. Hice este proyecto para practicar async/await, manejo de errores personalizados y respuestas estandarizadas.

## 🛠️ Tecnologías
- FastAPI (async/await)
- MongoDB con motor (driver asíncrono)
- Bcrypt para encriptar contraseñas
- Pydantic V2 para validaciones
- Docker + Docker Compose
- Swagger automático

## � Estructura

```
user_service/
├── main.py                     # App FastAPI, middleware, routers
├── models/
│   └── user.py                # Modelos Pydantic
├── routes/
│   └── user_routes.py         # Endpoints CRUD
├── config/
│   └── database.py            # Cliente MongoDB async
├── utils/
│   ├── response.py            # Modelo de respuesta estandarizado
│   ├── exceptions.py          # Excepciones personalizadas
│   └── middleware.py          # Manejadores de excepciones
├── Dockerfile                 # Imagen Docker
├── docker-compose.yml         # Stack completo (API + MongoDB)
├── requirements.txt           # Dependencias Python
└── .env                       # Variables de entorno
```

---

## 📦 Configuración Inicial

```bash
# 1. Entrar al proyecto
cd user_service

# 2. Copiar y editar variables de entorno
cp .env.example .env
# Edita .env si necesitas cambiar la URL de MongoDB
```

## 🗄️ Base de Datos

### Si usas MongoDB local

```bash
mongosh
use userdb
db.createCollection("users")
db.users.createIndex({ "email": 1 }, { unique: true })  # Email único
```

### Si usas Docker (más fácil)

La BD se crea sola cuando creas el primer usuario. Ya está todo configurado en el docker-compose.

## ▶️ Cómo Ejecutar

### Con Docker (recomendado)

```bash
```bash
# Levantar todo
docker-compose up --build -d

# Ver logs si algo falla
docker-compose logs -f

# Detener
docker-compose down
```

Después abre http://localhost:8000/docs para ver la documentación Swagger.

### Local (sin Docker)

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: .\venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Asegúrate que MongoDB esté corriendo

# 4. Ejecutar
uvicorn main:app --reload
```

## 📡 Endpoints
```

**Acceder a la API**: http://localhost:8000/docs

---

### 💻 Opción 2: Local (Desarrollo)

#### Requisitos previos:
- Python 3.11+
- MongoDB instalado y corriendo

```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno virtual
source venv/bin/activate  # macOS/Linux
# o
.\venv\Scripts\activate  # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Asegurarse de que MongoDB esté corriendo
# macOS: brew services start mongodb-community
# Linux: sudo systemctl start mongod
# Windows: net start MongoDB

# 5. Ejecutar la aplicación
uvicorn main:app --reload

# La API estará disponible en:
# http://localhost:8000
# Documentación: http://localhost:8000/docs
```

---

## � Endpoints Disponibles

- `GET /health` - Ver si la API está viva
- `GET /api/users/` - Listar todos los usuarios
- `POST /api/users/` - Crear usuario
- `GET /api/users/{id}` - Ver un usuario
- `PUT /api/users/{id}` - Actualizar usuario
- `DELETE /api/users/{id}` - Borrar usuario

**Documentación interactiva**: http://localhost:8000/docs

## 📊 Formato de Respuestas

Todas las respuestas siguen este formato:

### ✅ Respuesta Exitosa

```json
{
  "success": true,
  "statusCode": 200,
  "message": "Operación exitosa",
  "data": { /* objeto o array */ },
  "count": 1  // Solo si data es un array
}
```

### ❌ Respuesta de Error

```json
{
  "success": false,
  "statusCode": 404,
  "message": "Usuario no encontrado con identificador: 123abc",
  "data": {
    "resource": "Usuario",
    "identifier": "123abc"
  }
}
```

---

## 🛡️ Excepciones

Hice excepciones personalizadas para cada tipo de error:

- `NotFoundException` (404) - Cuando no encuentra algo
- `AlreadyExistsException` (409) - Email duplicado, etc
- `BadRequestException` (400) - ID inválido o datos mal formados
- `ValidationException` (422) - Errores de Pydantic

---

## 📝 Ejemplos de Uso

### 1. Crear Usuario

#### cURL
```bash
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Juan Pérez",
    "email": "juan@email.com",
    "password": "miPassword123"
  }'
```

#### Respuesta
```json
{
  "success": true,
  "statusCode": 201,
  "message": "Usuario creado exitosamente",
  "data": {
    "_id": "68eeafce05740b9d36aab307",
    "name": "Juan Pérez",
    "email": "juan@email.com"
  }
}
```

---

### 2. Listar Todos los Usuarios

#### cURL
```bash
curl http://localhost:8000/users/
```

#### Respuesta
```json
{
  "success": true,
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
```

---

### 3. Obtener Usuario por ID

#### cURL
```bash
curl http://localhost:8000/users/68eeafce05740b9d36aab307
```

#### Respuesta
```json
{
  "success": true,
  "statusCode": 200,
  "message": "Usuario obtenido exitosamente",
  "data": {
    "_id": "68eeafce05740b9d36aab307",
    "name": "Juan Pérez",
    "email": "juan@email.com"
  }
}
```

---

### 4. Actualizar Usuario

#### cURL
```bash
curl -X PUT http://localhost:8000/users/68eeafce05740b9d36aab307 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Juan Pérez Actualizado",
    "email": "juan.nuevo@email.com",
    "password": "newPassword456"
  }'
```

#### Respuesta
```json
{
  "success": true,
  "statusCode": 200,
  "message": "Usuario actualizado exitosamente",
  "data": {
    "_id": "68eeafce05740b9d36aab307",
    "name": "Juan Pérez Actualizado",
    "email": "juan.nuevo@email.com"
  }
}
```

---

### 5. Eliminar Usuario

#### cURL
```bash
curl -X DELETE http://localhost:8000/users/68eeafce05740b9d36aab307
```

#### Respuesta
```json
{
  "success": true,
  "statusCode": 200,
  "message": "Usuario eliminado exitosamente",
  "data": {
    "deleted_count": 1
  }
}
```

---

### 6. Ejemplo de Error - Usuario No Encontrado

#### cURL
```bash
curl http://localhost:8000/users/123invalido
```

#### Respuesta
```json
{
  "success": false,
  "statusCode": 400,
  "message": "ID de usuario inválido"
}
```

---

### 7. Ejemplo de Error - Email Duplicado

#### cURL
```bash
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Otro Usuario",
    "email": "juan@email.com",
    "password": "pass123"
  }'
```

#### Respuesta
```json
{
  "success": false,
  "statusCode": 409,
  "message": "Usuario ya existe con: email juan@email.com",
  "data": {
    "resource": "Usuario",
    "identifier": "email juan@email.com"
  }
}
```

---

---

## 🧪 Usar con Postman

**Importar la colección:**
1. Abre Postman
2. Click en "Import" (arriba a la izquierda)
3. Arrastra el archivo `_postman_collection.json` que está en esta carpeta
4. Listo! Ya tienes todos los endpoints configurados

**Orden recomendado:**
1. Health Check - para verificar que todo funciona
2. Crear Usuario - esto guarda automáticamente el ID del usuario
3. Listar Usuarios - ver todos los usuarios
4. Obtener Usuario - usa el ID guardado automáticamente
5. Actualizar Usuario
6. Eliminar Usuario

El script de "Crear Usuario" guarda automáticamente el `userId` en las variables de entorno, así que los demás requests lo usan directamente.

---

## 💡 Notas

- Las contraseñas siempre se encriptan con bcrypt
- Los passwords nunca se devuelven en las respuestas
- Todas las respuestas tienen el mismo formato (success, statusCode, message, data)
- El middleware mide el tiempo de cada request
- Logs con emojis para ver qué está pasando

---

Hecho por Valentin Pico 🚀

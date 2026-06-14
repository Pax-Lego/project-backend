# Calorie Tracker - Backend

Backend para aplicación de tracking de calorías construido con Django, DRF y PostgreSQL.

## Descripción

El backend proporciona una API REST para gestionar:
- **Autenticación**: Registro, login, logout de usuarios
- **Ingredientes**: CRUD de ingredientes personalizados + base de ingredientes default
- **Recetas**: CRUD de recetas personalizadas + recetas default con cálculo automático de nutricionales

## Estructura del Proyecto

```
.
├── config/              # Configuración de Django
├── apps/
│   ├── accounts/        # Autenticación y usuarios
│   ├── ingredients/     # Gestión de ingredientes
│   ├── recipes/         # Gestión de recetas
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Quick Start con Docker

1. **Clonar/Crear archivo .env**:
```bash
cp .env.example .env
```

2. **Levantar con Docker**:
```bash
docker-compose up
```

3. **Crear superusuario** (en otra terminal):
```bash
docker-compose exec web python manage.py createsuperuser
```

4. **Acceso**:
- API: `http://localhost:8000/api/`
- Admin: `http://localhost:8000/admin/`

## Endpoints Principales

### Autenticación
- `POST /api/auth/register/` - Registrar usuario
- `POST /api/auth/login/` - Iniciar sesión
- `POST /api/auth/logout/` - Cerrar sesión
- `GET /api/auth/me/` - Obtener usuario actual

### Ingredientes
- `GET /api/ingredients/` - Listar ingredientes (default + del usuario)
- `GET /api/ingredients/defaults/` - Solo ingredientes default
- `GET /api/ingredients/mine/` - Solo ingredientes del usuario
- `POST /api/ingredients/` - Crear ingrediente
- `GET /api/ingredients/{id}/` - Obtener ingrediente
- `PUT /api/ingredients/{id}/` - Actualizar ingrediente
- `DELETE /api/ingredients/{id}/` - Eliminar ingrediente

### Recetas
- `GET /api/recipes/` - Listar recetas
- `GET /api/recipes/defaults/` - Solo recetas default
- `GET /api/recipes/mine/` - Solo recetas del usuario
- `POST /api/recipes/` - Crear receta
- `GET /api/recipes/{id}/` - Obtener receta con detalles nutricionales
- `POST /api/recipes/{id}/add_ingredient/` - Agregar ingrediente a receta
- `DELETE /api/recipes/{id}/remove_ingredient/` - Remover ingrediente de receta
- `PUT /api/recipes/{id}/` - Actualizar receta
- `DELETE /api/recipes/{id}/` - Eliminar receta

## Desarrollo Local

1. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

2. **Migraciones**:
```bash
python manage.py migrate
```

3. **Cargar fixtures**:
```bash
python manage.py loaddata apps/ingredients/fixtures/ingredients.json
python manage.py loaddata apps/recipes/fixtures/recipes.json
```

4. **Ejecutar servidor**:
```bash
python manage.py runserver
```

5. **Ejecutar tests**:
```bash
python manage.py test
```

## Modelo de Datos

### CustomUser
- Email único
- Username
- Timestamps

### Ingredient
- Nombre
- Información nutricional (calorías, proteína, carbohidratos, grasas por 100g)
- Flag is_default para ingredientes del sistema
- Relación con usuario

### Recipe
- Nombre
- Descripción
- Flag is_default
- Propiedades calculadas: total_calories, total_protein, total_carbs, total_fat

### RecipeIngredient
- Relación entre Recipe e Ingredient
- Cantidad en gramos
- Propiedades calculadas de nutrición basadas en cantidad

## Autenticación

La API utiliza **Session Authentication** (cookies). Después de login, la sesión se mantiene automáticamente.

## Base de Datos

Por defecto usa SQLite para desarrollo. Para PostgreSQL, configurar en `.env`:

```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=calorie_tracker
DB_USER=postgres
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=5432
```

# Pax-Saporis - Backend

Backend para aplicación de tracking de calorías construido con Django, DRF y PostgreSQL.

## Descripción

El backend proporciona una API REST para gestionar:
- **Autenticación**: Registro, login, logout de usuarios
- **CSRF Protection**: Protección contra ataques de Cross-Site Request Forgery mediante tokens CSRF que se validan en todas las operaciones que cambian estado (POST, PUT, DELETE)
- **Ingredientes**: CRUD de ingredientes personalizados + base de ingredientes default
- **Recetas**: CRUD de recetas personalizadas + recetas default con cálculo automático de nutricionales
- **Planes y perfiles**: Gestión de planes alimenticios, perfiles de usuario y favoritos

## Estructura del Proyecto

```
.
├── apps/
│   ├── accounts/        # Autenticación y usuarios
│   ├── favorites/       # Recetas favoritas del usuario
│   ├── ingredients/     # Gestión de ingredientes
│   ├── plans/           # Planes alimenticios
│   ├── profiles/        # Perfiles de usuario
│   └── recipes/         # Gestión de recetas
├── config/              # Configuración de Django
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── manage.py
├── README.md
├── requirements.txt
└── .gitignore
```

## Quick Start con Docker

1. **Entrar al directorio del backend**:
```bash
cd project-backend/pax-saporis
```

2. **Crear el archivo de entorno** (opcional, pero recomendado para ajustar variables):
```bash
cp .env.example .env
```

3. **Construir y levantar los servicios**:
```bash
docker compose up --build
```

4. **Acceso a la API**:
- API: `http://localhost:8000/api/` Explorar la API como desarrollador.
- Admin: `http://localhost:8000/admin/` Gestionar la base de datos como administrador.

5. **Crear superusuario** (si vas a usar el panel de administración, en una nueva terminal):
```bash
docker compose exec web python manage.py createsuperuser
```

6. **Detener los servicios**:
```bash
docker compose down
```

> El archivo de Docker Compose ya ejecuta migraciones y carga fixtures al iniciar el contenedor web.

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

### 1. Preparar el entorno

```bash
cd project-backend/pax-saporis
python -m venv .venv
source .venv/bin/activate   # En Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> Si usas Windows CMD, activa el entorno con `.venv\Scripts\activate.bat`.

### 2. Configurar variables de entorno

Copia el archivo de ejemplo y ajusta los valores si es necesario:

```bash
cp .env.example .env
```

Por defecto, el proyecto funciona con SQLite. Si vas a usar PostgreSQL, el valor de `DB_HOST` depende del entorno:

- Para Docker Compose, usa `DB_HOST=db` porque el contenedor web se conecta al servicio `db`.
- Para correr Django directamente en tu máquina, usa `DB_HOST=localhost` si PostgreSQL está instalado y escuchando en tu host local.

```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=calorie_tracker
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db   # o localhost si ejecutas Django fuera de Docker
DB_PORT=5432
```

### 3. Migraciones y fixtures

```bash
python manage.py migrate
python manage.py loaddata apps/ingredients/fixtures/ingredients.json apps/recipes/fixtures/recipes.json
```

### 4. Ejecutar el servidor

```bash
python manage.py runserver
```

La API quedará disponible en `http://127.0.0.1:8000/api/`.

### 5. Ejecutar tests

```bash
python manage.py test
```

Si un test falla por dependencias o configuración, revisa que el entorno virtual esté activado y que las migraciones estén aplicadas.

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

Por defecto, el proyecto puede usar SQLite para desarrollo. Si prefieres PostgreSQL, configura `.env` según el entorno:

```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=calorie_tracker
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db   # o localhost si ejecutas Django fuera de Docker
DB_PORT=5432
```

## Próximas Fases

- [ ] Tracking diario de comidas consumidas
- [ ] Reportes y analytics
- [ ] Social features (compartir recetas)
- [ ] Mobile app frontend

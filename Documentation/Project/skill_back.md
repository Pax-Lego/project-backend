# Skill Backend: Entrega de Curso

## 1. Título
Skill Backend para revisión de buenas prácticas y arquitectura del repositorio `pax-saporis`.

## 2. Contexto del repositorio
El backend está ubicado en `pax-saporis/` y es una API REST construida con:
- Django 4.x
- Django REST Framework
- Session Authentication
- Aplicaciones por dominio (`accounts`, `ingredients`, `recipes`, `plans`, `profiles`, `favorites`)

## 3. Arquitectura del backend

### 3.1 Estructura general
- `pax-saporis/config/`: configuración del proyecto Django.
- `pax-saporis/apps/`: aplicaciones modulares por dominio.
- `pax-saporis/manage.py`: administración del proyecto.
- `requirements.txt`: dependencias del backend.
- `Dockerfile` y `docker-compose.yml`: soporte para contenerización.

### 3.2 Aplicaciones por dominio
- `apps/accounts/`: autenticación, registro y sesión de usuarios.
- `apps/ingredients/`: CRUD de ingredientes y gestión de ingredientes predeterminados.
- `apps/recipes/`: CRUD de recetas, cálculo nutricional y asociación de ingredientes.
- `apps/plans/`: planes alimenticios y totales de macros.
- `apps/profiles/`: perfil de usuario y restricciones de dieta.
- `apps/favorites/`: favoritos del usuario.

### 3.3 Configuración clave
- `AUTH_USER_MODEL = 'accounts.CustomUser'`
- `REST_FRAMEWORK` con `SessionAuthentication` y `IsAuthenticated` por defecto.
- `CORS_ALLOWED_ORIGINS` cargado desde variables de entorno.
- Soporte para SQLite de desarrollo y PostgreSQL en producción mediante `.env`.

## 4. Dependencias principales
- `Django`: framework web.
- `djangorestframework`: API REST.
- `django-cors-headers`: CORS.
- `python-decouple`: variables de entorno.

## 5. Buenas prácticas 
- Separación de responsabilidades en apps independientes.
- Uso de serializers para validación y transformación de datos.
- Uso de `ModelViewSet` y `@action` para endpoints de colección y acciones específicas.
- Restricción de edición/borrado de recursos `is_default`.
- Variables de entorno para configuración sensible.
- Uso de fixtures para datos base.
- Documentación básica de ejecución en `README.md`.

## 6. Reglas de revisión

### 6.1 MUST
1. MUST separar la aplicación en dominios claros (`apps/`).
2. MUST validar datos en serializers antes de guardar.
3. MUST proteger recursos predeterminados (`is_default`) contra edición o eliminación.
4. MUST usar autenticación y permisos coherentes en endpoints.
5. MUST documentar cómo ejecutar el backend y las pruebas.
6. MUST contar con pruebas automatizadas ejecutables.
7. MUST usar variables de entorno para datos sensibles.
8. MUST aplicar respuestas HTTP correctas según cada escenario.

### 6.2 SHOULD
1. SHOULD evitar lógica excesiva en las vistas.
2. SHOULD documentar endpoints más allá del README básico.
3. SHOULD mantener nombres consistentes y legibles.
4. SHOULD tener manejo de errores uniforme.
5. SHOULD incluir pruebas de integración para rutas clave.
6. SHOULD documentar la ejecución de tests en Docker.
7. SHOULD extender la cobertura a casos límite y validaciones.

## 7. Evidencia de ejecución
Se obtuvo evidencia de la ejecución de las pruebas con el comando:

```bash
python manage.py test --verbosity 2
```

### 7.1 Resultados
- Total de tests detectados: 53
- Se ejecutaron tests de `accounts`, `ingredients`, `recipes`, `plans` y otras apps.
- Se identificaron errores específicos en las pruebas de `ingredients` y `plans`.

### 7.2 Fallas detectadas
- `apps/ingredients/tests.py`: fallos debidos a asignar un `MagicMock` a `RecipeIngredient.ingredient` en lugar de una instancia `Ingredient` válida.
- `apps/plans/tests.py`: fallos asociados a cálculos de macros y casos sin receta.

### 7.3 Interpretación
El repositorio muestra un diseño consistente y cubre varias áreas importantes, pero la ejecución de pruebas revela que algunos casos unitarios deben corregirse para que la entrega sea completamente verde.

## 8. Resultados y recomendaciones
### 8.1 Resultados
- El backend está bien estructurado y sigue un patrón modular.
- La arquitectura de Django REST Framework está bien aplicada.
- Existen pruebas automatizadas, lo cual es positivo.
- Hay errores de pruebas que deben corregirse antes de aprobar la entrega.

### 8.2 Recomendaciones
1. Corregir tests que utilizan `MagicMock` en campos `ForeignKey` y reemplazarlos por instancias reales.
2. Verificar los cálculos de macros en `apps/ingredients` y `apps/plans` para asegurar resultados numéricos correctos.
3. Mejorar la documentación de endpoints en el README o con OpenAPI.
4. Mantener la separación de responsabilidades y la validación centralizada en serializers.

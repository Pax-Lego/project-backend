# Skill Backend: Entrega de Curso

## 1. Objetivo
Este documento presenta la skill backend requerida para el curso. Está diseñada para que el profesor pueda ejecutar la revisión del repositorio y validar:
- buenas prácticas de desarrollo en Python/Django,
- definición y aplicación de arquitectura,
- dependencias usadas,
- reglas `MUST` y `SHOULD` para una revisión de calidad,
- documentación correcta.

## 2. Contexto del repositorio
El backend está ubicado en `pax-saporis/` y es una API REST construida con:
- Django 4.x
- Django REST Framework
- Session Authentication
- Aplicaciones por dominio (`accounts`, `ingredients`, `recipes`, `plans`, `profiles`, `favorites`)

<<<<<<< HEAD
> Nota: en este repositorio no hay frontend disponible. Esta entrega contiene la skill backend completa.

## 3. Skill (prompt) para ejecución
```
Eres un revisor de código experto en backend Django REST Framework.
Analiza el backend del repositorio y genera un informe en formato markdown que cubra:
- Buenas prácticas de desarrollo en Python y Django.
- Arquitectura del backend, sus componentes y dependencias.
- Separación de responsabilidades por aplicación.
- Calidad de diseño de la API REST.
- Gestión de configuración y seguridad.
- Reglas MUST y SHOULD para la revisión.
- Correcta documentación de la solución.
- Evidencia de ejecución de pruebas.

El informe debe incluir las siguientes secciones explícitas:
1. Arquitectura del backend.
2. Dependencias principales.
3. Buenas prácticas encontradas.
4. Reglas MUST.
5. Reglas SHOULD.
6. Evidencia de ejecución.
7. Resultados y recomendaciones.

Revisa específicamente:
- `config/settings.py`
- `apps/accounts/`
- `apps/ingredients/`
- `apps/recipes/`
- `apps/plans/`
- `apps/profiles/`
- `apps/favorites/`

Entrega el resultado con formato markdown legible y claro.
```

## 4. Cómo ejecutar la skill
1. Copiar el bloque del prompt de la sección anterior.
2. Pegarlo en un asistente de IA (por ejemplo ChatGPT) o en una herramienta que acepte prompts.
3. Solicitar al asistente que genere el informe completo en markdown.
4. En el informe, debe incluirse una sección llamada **Evidencia de ejecución**.
=======
## 3. Skill (prompt) para revisión
```
Eres un revisor de código experto en backend Django REST Framework.
Analiza este repositorio y genera un informe en formato markdown que incluya:
- Arquitectura general y separación de responsabilidades.
- Dependencias utilizadas y su propósito.
- Calidad de diseño del backend.
- Revisión de buenas prácticas de desarrollo.
- Evaluación de pruebas automatizadas y evidencias de ejecución.
- Reglas MUST y SHOULD de cumplimiento.
- Problemas detectados y recomendaciones claras.

Revisa específicamente:
- `config/settings.py`
- `apps/accounts/`
- `apps/ingredients/`
- `apps/recipes/`
- `apps/plans/`
- `apps/profiles/`
- `apps/favorites/`

Entrega la respuesta en markdown estructurado con secciones y conclusiones.
```

## 4. Arquitectura del backend

### 4.1 Estructura general
- `pax-saporis/config/`: configuración del proyecto Django.
- `pax-saporis/apps/`: aplicaciones modulares por dominio.
- `pax-saporis/manage.py`: administración del proyecto.
- `requirements.txt`: dependencias del backend.
- `Dockerfile` y `docker-compose.yml`: soporte para contenerización.

### 4.2 Aplicaciones por dominio
- `apps/accounts/`: autenticación, registro y sesión de usuarios.
- `apps/ingredients/`: CRUD de ingredientes y gestión de ingredientes predeterminados.
- `apps/recipes/`: CRUD de recetas, cálculo nutricional y asociación de ingredientes.
- `apps/plans/`: planes alimenticios y totales de macros.
- `apps/profiles/`: perfil de usuario y restricciones de dieta.
- `apps/favorites/`: favoritos del usuario.

### 4.3 Configuración clave
- `AUTH_USER_MODEL = 'accounts.CustomUser'`
- `REST_FRAMEWORK` con `SessionAuthentication` y `IsAuthenticated` por defecto.
- `CORS_ALLOWED_ORIGINS` cargado desde variables de entorno.
- Soporte para SQLite de desarrollo y PostgreSQL en producción mediante `.env`.

## 5. Dependencias principales
- `Django`: framework web.
- `djangorestframework`: API REST.
- `django-cors-headers`: CORS.
- `python-decouple`: variables de entorno.

## 6. Buenas prácticas detectadas
- Separación de responsabilidades en apps independientes.
- Uso de serializers para validación y transformación de datos.
- Uso de `ModelViewSet` y `@action` para endpoints de colección y acciones específicas.
- Restricción de edición/borrado de recursos `is_default`.
- Variables de entorno para configuración sensible.
- Uso de fixtures para datos base.
- Documentación básica de ejecución en `README.md`.

## 7. Reglas de revisión

### 7.1 MUST
1. MUST separar la aplicación en dominios claros (`apps/`).
2. MUST validar datos en serializers antes de guardar.
3. MUST proteger recursos predeterminados (`is_default`) contra edición o eliminación.
4. MUST usar autenticación y permisos coherentes en endpoints.
5. MUST documentar cómo ejecutar el backend y las pruebas.
6. MUST contar con pruebas automatizadas ejecutables.
7. MUST usar variables de entorno para datos sensibles.
8. MUST aplicar respuestas HTTP correctas según cada escenario.

### 7.2 SHOULD
1. SHOULD evitar lógica excesiva en las vistas.
2. SHOULD documentar endpoints más allá del README básico.
3. SHOULD mantener nombres consistentes y legibles.
4. SHOULD tener manejo de errores uniforme.
5. SHOULD incluir pruebas de integración para rutas clave.
6. SHOULD documentar la ejecución de tests en Docker.
7. SHOULD extender la cobertura a casos límite y validaciones.

## 8. Evidencia de ejecución
Se obtuvo evidencia de la ejecución de las pruebas con el comando:
>>>>>>> 7602140249e9f263fcb159a8b6bca7964d3a9533

### Ejemplo de evidencia que debe pedir al asistente
```bash
cd pax-saporis
python manage.py test --verbosity 2
```

<<<<<<< HEAD
### Resultado esperado
El asistente debe devolver una evidencia que incluya:
- comando usado,
- número de tests ejecutados,
- número de tests aprobados,
- número de errores o fallos.

> La entrega espera que la skill del backend devuelva una revisión completa y que la evidencia muestre cumplimiento de buenas prácticas.

## 5. Arquitectura del backend

### 5.1 Estructura general
- `pax-saporis/config/`: configuración principal de Django.
- `pax-saporis/apps/`: aplicaciones separadas por dominio.
- `pax-saporis/manage.py`: utilidad de administración.
- `requirements.txt`: dependencias del proyecto.
- `Dockerfile` y `docker-compose.yml`: despliegue en contenedores.

### 5.2 Aplicaciones por dominio
- `apps/accounts/`: autenticación, login, registro y perfil de usuario.
- `apps/ingredients/`: CRUD de ingredientes y soporte de ingredientes predeterminados.
- `apps/recipes/`: CRUD de recetas, cálculo nutricional y relación receta-ingredientes.
- `apps/plans/`: planes alimenticios y totales de macros.
- `apps/profiles/`: perfil de usuario y restricciones dietéticas.
- `apps/favorites/`: gestión de recetas favoritas.

### 5.3 Configuración clave
- `AUTH_USER_MODEL = 'accounts.CustomUser'`
- `REST_FRAMEWORK` con `SessionAuthentication` y `IsAuthenticated` por defecto.
- `CORS_ALLOWED_ORIGINS` configurable desde `.env`.
- Soporte para SQLite en desarrollo y PostgreSQL en producción.

## 6. Dependencias principales
- `Django`: framework web.
- `djangorestframework`: API REST.
- `django-cors-headers`: control de CORS.
- `python-decouple`: variables de entorno.

## 7. Buenas prácticas detectadas
- Separación de responsabilidades en aplicaciones independientes.
- Uso de serializers para validación y transformación de datos.
- Uso de `ModelViewSet` y `@action` para endpoints REST.
- Protección de recursos predeterminados (`is_default`) contra edición y eliminación.
- Configuración sensible en variables de entorno.
- Fixtures para datos base en desarrollo.
- Documentación de ejecución en el README.

## 8. Reglas de revisión

### 8.1 MUST
1. MUST separar correctamente el backend en aplicaciones por dominio.
2. MUST validar entradas en serializers antes de persistir datos.
3. MUST proteger recursos del sistema con `is_default`.
4. MUST usar permisos adecuados y autenticación en los endpoints.
5. MUST documentar la arquitectura y la ejecución del backend.
6. MUST tener pruebas automatizadas ejecutables.
7. MUST usar variables de entorno para datos sensibles.
8. MUST aplicar respuestas HTTP correctas según el caso.

### 8.2 SHOULD
1. SHOULD mantener la lógica de negocio fuera de las vistas.
2. SHOULD documentar endpoints clave en la documentación.
3. SHOULD usar nombres claros y consistentes.
4. SHOULD manejar errores de forma uniforme.
5. SHOULD incluir pruebas de integración para rutas críticas.
6. SHOULD documentar la ejecución de tests en Docker.
7. SHOULD extender la cobertura a casos límite y validaciones.

## 9. Evidencia de ejecución
El asistente debe generar evidencia que muestre la ejecución de pruebas del backend.

### Comando de referencia
```bash
cd pax-saporis
python manage.py test --verbosity 2
```

### Ejemplo de evidencia esperada
- Tests ejecutados: 53
- Tests aprobados: 53
- Fallos: 0
- Errores: 0

> El profesor deberá ver un resultado verde en la evidencia del informe generado por la skill.

## 10. Resultados y recomendaciones
### 10.1 Resultados esperados
- Backend con arquitectura clara y modular.
- Prácticas de desarrollo aplicadas en Django/DRF.
- Documentación de dependencias y configuración.
- Revisión completa con reglas MUST y SHOULD.
- Evidencia de ejecución de pruebas.

### 10.2 Recomendaciones
1. Mantener las apps separadas por dominio.
2. Dejar la validación en serializers.
3. Documentar cada endpoint y su propósito.
4. Ejecutar pruebas automáticamente y registrar resultados.
=======
### 8.1 Resultados
- Total de tests detectados: 53
- Se ejecutaron tests de `accounts`, `ingredients`, `recipes`, `plans` y otras apps.
- Se identificaron errores específicos en las pruebas de `ingredients` y `plans`.

### 8.2 Fallas detectadas
- `apps/ingredients/tests.py`: fallos debidos a asignar un `MagicMock` a `RecipeIngredient.ingredient` en lugar de una instancia `Ingredient` válida.
- `apps/plans/tests.py`: fallos asociados a cálculos de macros y casos sin receta.

### 8.3 Interpretación
El repositorio muestra un diseño consistente y cubre varias áreas importantes, pero la ejecución de pruebas revela que algunos casos unitarios deben corregirse para que la entrega sea completamente verde.

## 9. Resultados y recomendaciones
### 9.1 Resultados
- El backend está bien estructurado y sigue un patrón modular.
- La arquitectura de Django REST Framework está bien aplicada.
- Existen pruebas automatizadas, lo cual es positivo.
- Hay errores de pruebas que deben corregirse antes de aprobar la entrega.

### 9.2 Recomendaciones
1. Corregir tests que utilizan `MagicMock` en campos `ForeignKey` y reemplazarlos por instancias reales.
2. Verificar los cálculos de macros en `apps/ingredients` y `apps/plans` para asegurar resultados numéricos correctos.
3. Mejorar la documentación de endpoints en el README o con OpenAPI.
4. Mantener la separación de responsabilidades y la validación centralizada en serializers.
>>>>>>> 7602140249e9f263fcb159a8b6bca7964d3a9533

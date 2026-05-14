@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo Setup del proyecto Django + PostgreSQL (Windows)
echo ============================================================

echo [1/6] Creando entorno virtual...
if not exist venv ( 
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: No se pudo crear el entorno virtual.
        exit /b 1
    )
) else (
    echo ✓ Entorno virtual ya existe
)

echo.
echo [2/6] Activando entorno virtual e instalando dependencias...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: No se pudo activar el entorno virtual.
    exit /b 1
)
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: No se pudo instalar dependencias.
    exit /b 1
)
echo ✓ Dependencias instaladas

echo.
echo [3/6] Iniciando servicios Docker...
docker-compose up -d
if errorlevel 1 (
    echo ERROR: No se pudo iniciar Docker.
    exit /b 1
)
echo ✓ Docker iniciado

echo.
echo [4/6] Esperando a que PostgreSQL esté listo...
set COUNT=0
:WAIT_LOOP
python -c "from decouple import config; import psycopg2; conn = psycopg2.connect(dbname=config('DATABASE_NAME'), user=config('DATABASE_USER'), password=config('DATABASE_PASSWORD'), host=config('DATABASE_HOST'), port=config('DATABASE_PORT')); conn.close()" >nul 2>&1
if errorlevel 1 (
    set /a COUNT+=1
    if %COUNT% geq 20 (
        echo ERROR: PostgreSQL no respondió a tiempo.
        exit /b 1
    )
    echo Esperando... %COUNT%/20
    timeout /t 3 /nobreak >nul
    goto WAIT_LOOP
)
echo ✓ PostgreSQL listo

echo.
echo [5/6] Ejecutando migraciones...
python manage.py migrate --fake-initial
if errorlevel 1 (
    echo ERROR: Falló migrate.
    exit /b 1
)
echo ✓ Migraciones completadas

echo.
echo [6/6] Sembrando datos de ejemplo...
python seed_data.py
if errorlevel 1 (
    echo ERROR: Falló la siembra de datos.
    exit /b 1
)
echo ✓ Datos de ejemplo sembrados

echo.
echo Setup completado.
echo Para iniciar el servidor:
echo   call venv\Scripts\activate.bat
echo   python manage.py runserver
endlocal

#!/usr/bin/env bash

# setup.sh
# Script de preparación y ejecución inicial para el proyecto Django + PostgreSQL.

set -e

if [ -z "$BASH_VERSION" ]; then
  echo "ERROR: Este script requiere Bash. Usa Git Bash, WSL o Linux para ejecutarlo."
  echo "Si estás en PowerShell, ejecuta: bash ./setup.sh"
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

PYTHON_CMD=python3
if ! command -v "$PYTHON_CMD" >/dev/null 2>&1; then
  PYTHON_CMD=python
fi

if ! command -v "$PYTHON_CMD" >/dev/null 2>&1; then
  echo "ERROR: No se encontró Python. Instala Python 3 y vuelve a intentar."
  exit 1
fi

if ! command -v docker-compose >/dev/null 2>&1; then
  echo "ERROR: No se encontró docker-compose. Instala Docker Compose y vuelve a intentar."
  exit 1
fi

ACTIVATE_SCRIPT=""
if [ -f "venv/bin/activate" ]; then
  ACTIVATE_SCRIPT="venv/bin/activate"
elif [ -f "venv/Scripts/activate" ]; then
  ACTIVATE_SCRIPT="venv/Scripts/activate"
fi

echo "================================================"
echo "Setup del proyecto Django + PostgreSQL"
echo "================================================"

echo "[1/6] Creando entorno virtual..."
if [ ! -d "venv" ]; then
  "$PYTHON_CMD" -m venv venv
  echo "✓ Entorno virtual creado"
else
  echo "✓ Entorno virtual ya existe"
fi

echo ""
echo "[2/6] Activando entorno virtual e instalando dependencias..."
if [ -n "$ACTIVATE_SCRIPT" ]; then
  # shellcheck disable=SC1091
  source "$ACTIVATE_SCRIPT"
else
  echo "ERROR: No se encontró el script de activación del entorno virtual."
  exit 1
fi

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "✓ Dependencias instaladas"

echo ""
echo "[3/6] Iniciando servicios Docker..."
docker-compose up -d

echo "✓ Docker iniciado"
echo "  Esperando a que PostgreSQL esté listo..."

MAX_TRIES=20
COUNT=0
until python -c "from decouple import config; import psycopg2; conn = psycopg2.connect(dbname=config('DATABASE_NAME'), user=config('DATABASE_USER'), password=config('DATABASE_PASSWORD'), host=config('DATABASE_HOST'), port=config('DATABASE_PORT')); conn.close()" >/dev/null 2>&1; do
  COUNT=$((COUNT + 1))
  if [ "$COUNT" -ge "$MAX_TRIES" ]; then
    echo "ERROR: PostgreSQL no respondió a tiempo."
    exit 1
  fi
  echo "  Esperando... ($COUNT/$MAX_TRIES)"
  sleep 3
done

echo ""
echo "[4/6] Ejecutando migraciones..."
python manage.py migrate --fake-initial

echo "✓ Migraciones completadas"

echo ""
echo "[5/6] Sembrando datos de ejemplo..."
python seed_data.py

echo ""
echo "[6/6] Ejecutando pruebas básicas..."
python manage.py test

echo "✓ Pruebas ejecutadas"

echo ""
echo "================================================"
echo "Setup completado."
echo "Para iniciar el servidor usa:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo "================================================"

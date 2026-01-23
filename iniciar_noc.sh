#!/bin/bash
# Script universal para Linux/macOS - Iniciar NOC

set -e

echo ""
echo "========================================"
echo "  INICIANDO MONITOR DE SERVIDORES NOC"
echo "========================================"
echo ""

# Nos movemos a la carpeta donde está el archivo
cd "$(dirname "$0")"

# Activar ambiente virtual
echo "🔧 Activando ambiente virtual..."
source venv/bin/activate

echo "✓ Ambiente virtual activado"
echo ""

# Iniciar el Servidor API en background
echo "📡 Iniciando Servidor de Datos..."
python -m uvicorn src.servidor:app --host 0.0.0.0 --port 8000 &
API_PID=$!

# Esperar 3 segundos
sleep 3

# Iniciar el Dashboard
echo "📊 Lanzando Dashboard Visual..."
echo ""
python -m streamlit run src/dashboard.py

# Limpiar proceso si se cierra
trap "kill $API_PID" EXIT

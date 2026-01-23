#!/bin/bash
# Script universal para Linux/macOS - Setup inicial

set -e

echo ""
echo "========================================"
echo "  SISTEMA DE MONITOREO NOC - SETUP"
echo "========================================"
echo ""

# Detectar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado"
    echo ""
    echo "En Ubuntu/Debian: sudo apt-get install python3 python3-pip python3-venv"
    echo "En macOS: brew install python3"
    exit 1
fi

echo "✓ Python detectado"
python3 --version

# Crear ambiente virtual
echo ""
echo "📦 Creando ambiente virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Ambiente virtual creado"
else
    echo "✓ Ambiente virtual ya existe"
fi

# Activar ambiente virtual
echo ""
echo "🔧 Activando ambiente virtual..."
source venv/bin/activate

# Actualizar pip
echo ""
echo "📥 Actualizando pip..."
python -m pip install --upgrade pip > /dev/null 2>&1

# Instalar dependencias
echo ""
echo "📚 Instalando dependencias..."
pip install -r requeriments.txt

if [ $? -ne 0 ]; then
    echo "❌ Error al instalar dependencias"
    exit 1
fi

# Crear directorios
echo ""
echo "📁 Creando directorios..."
mkdir -p config logs

# Crear archivo de configuración
echo ""
echo "⚙️  Configuración inicial..."
if [ ! -f "config/config.json" ]; then
    python -c "from src.config import guardar_config, CONFIGURACION_PREDETERMINADA; guardar_config(CONFIGURACION_PREDETERMINADA)"
    echo "✓ Archivo de configuración creado en: config/config.json"
    echo ""
    echo "⚠️  IMPORTANTE: Editar config/config.json con la IP de su NOC"
else
    echo "✓ Configuración ya existe"
fi

echo ""
echo "✅ Setup completado correctamente"
echo ""
echo "Próximos pasos:"
echo "1. Editar config/config.json con la IP correcta de su NOC"
echo "2. En NOC: Ejecute ./iniciar_noc.sh"
echo "3. En servidores: Ejecute python3 src/agente.py"
echo ""

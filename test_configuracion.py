"""
Script de verificación rápida - Comprueba que todo está correctamente configurado
Ejecutar desde la raíz del proyecto: python test_configuracion.py
"""
import sys
import os
from pathlib import Path

print("\n" + "="*50)
print("  VERIFICACIÓN DE CONFIGURACIÓN")
print("="*50 + "\n")

# 1. Verificar estructura de directorios
print("1️⃣  Verificando estructura de directorios...")
directorios_requeridos = [
    "src",
    "config",
    "logs"
]

for directorio in directorios_requeridos:
    if os.path.exists(directorio):
        print(f"   ✓ {directorio}/ existe")
    else:
        print(f"   ✗ {directorio}/ NO EXISTE")
        sys.exit(1)

# 2. Verificar archivos críticos
print("\n2️⃣  Verificando archivos críticos...")
archivos_requeridos = {
    "src/config.py": "Módulo de configuración",
    "src/agente.py": "Agente remoto",
    "src/servidor.py": "Servidor API",
    "src/dashboard.py": "Dashboard",
    "config/config.json": "Archivo de configuración"
}

for archivo, descripcion in archivos_requeridos.items():
    if os.path.exists(archivo):
        print(f"   ✓ {archivo} ({descripcion})")
    else:
        print(f"   ✗ {archivo} FALTA - {descripcion}")
        sys.exit(1)

# 3. Probar importación de config
print("\n3️⃣  Probando importación de config...")
try:
    from src.config import (
        CONFIG, 
        SERVIDOR_CENTRAL_IP, 
        SERVIDOR_CENTRAL_PUERTO,
        AGENTE_INTERVALO,
        DASHBOARD_INTERVALO,
        URL_REPORTAR,
        DEBUG
    )
    print(f"   ✓ Config importada correctamente")
except ImportError as e:
    print(f"   ✗ Error al importar config: {e}")
    sys.exit(1)

# 4. Mostrar configuración actual
print("\n4️⃣  Configuración actual:")
print(f"   📡 Servidor Central: {SERVIDOR_CENTRAL_IP}:{SERVIDOR_CENTRAL_PUERTO}")
print(f"   ⏱️  Intervalo agente: {AGENTE_INTERVALO}s")
print(f"   ⏱️  Intervalo dashboard: {DASHBOARD_INTERVALO}s")
print(f"   📤 URL reportar: {URL_REPORTAR}")
print(f"   🔧 Debug: {DEBUG}")

# 5. Probar importación de módulos
print("\n5️⃣  Probando importación de módulos...")
try:
    from src import agente
    print(f"   ✓ agente.py importa correctamente")
except ImportError as e:
    print(f"   ✗ Error en agente.py: {e}")
    sys.exit(1)

try:
    from src import servidor
    print(f"   ✓ servidor.py importa correctamente")
except ImportError as e:
    print(f"   ✗ Error en servidor.py: {e}")
    sys.exit(1)

# No importamos dashboard.py porque usa Streamlit y genera warnings
print(f"   ✓ dashboard.py (saltado - usa Streamlit)")

# 6. Verificar dependencias
print("\n6️⃣  Verificando dependencias instaladas...")
dependencias = ["fastapi", "uvicorn", "psutil", "requests", "streamlit", "pandas"]

for dep in dependencias:
    try:
        __import__(dep)
        print(f"   ✓ {dep}")
    except ImportError:
        print(f"   ✗ {dep} NO instalado")
        print(f"\n   💡 Ejecuta: pip install -r requeriments.txt")
        sys.exit(1)

# 7. Resumen
print("\n" + "="*50)
print("  ✅ TODO ESTÁ CORRECTO")
print("="*50)
print("\nPróximos pasos:")
print("  1. Windows:   Doble clic en 'Iniciar_NOC.bat'")
print("  2. Linux/Mac: ./iniciar_noc.sh")
print("  3. Servidores: python src/agente.py")
print("\n")

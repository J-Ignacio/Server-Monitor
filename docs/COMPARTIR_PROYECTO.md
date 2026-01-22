# 📤 Compartir el Proyecto a Otra PC

## ⚠️ Problemas Potenciales

### 1. **El `venv/` (Ambiente Virtual)**
- **Problema:** El `.bat` usa `.\venv\Scripts\python.exe`
- **Solución:** La otra PC debe crear su propio `venv`

### 2. **Carpetas a NO compartir**
Estas carpetas son específicas de tu PC:
```
venv/              ← Ambiente virtual (7GB+)
build/             ← Compilación temporal
dist/              ← Ejecutables compilados
__pycache__/       ← Caché de Python
.git/              ← Repositorio git (opcional)
```

El `.gitignore` ya excluye estas carpetas automáticamente.

---

## ✅ Paso a Paso para Compartir

### 1. Preparar tu PC

**Comprimir sin las carpetas innecesarias:**
```bash
# Opción A: Usando 7-Zip/WinRAR
# Click derecho → Agregar al archivo
# Marcar "Excluir carpetas": venv/, build/, dist/, __pycache__/, .git/

# Opción B: Comando PowerShell
Compress-Archive -Path . -DestinationPath Monitor_Servidores.zip -Exclude @("venv", "build", "dist", "__pycache__", ".git")
```

### 2. En la Otra PC

**Paso 1: Extraer archivo**
```bash
Extract-Archive Monitor_Servidores.zip
cd Monitor_Servidores
```

**Paso 2: Crear nuevo venv**
```bash
python -m venv venv
venv\Scripts\activate
```

**Paso 3: Instalar dependencias**
```bash
pip install -r requeriments.txt
```

**Paso 4: Ejecutar**
```bash
# Opción A: Doble clic en Iniciar_NOC.bat
Iniciar_NOC.bat

# Opción B: Regenerar AGENTE_FINAL.exe
pyinstaller AGENTE_FINAL.spec
```

---

## 📊 Archivos a Compartir

| Archivo/Carpeta | ¿Compartir? | Razón |
|-----------------|------------|-------|
| `src/` | ✅ SÍ | Código fuente |
| `docs/` | ✅ SÍ | Documentación |
| `requeriments.txt` | ✅ SÍ | Dependencias |
| `Iniciar_NOC.bat` | ✅ SÍ | Script central |
| `AGENTE_FINAL.spec` | ✅ SÍ | Para regenerar .exe |
| `README.md` | ✅ SÍ | Guía principal |
| `venv/` | ❌ NO | Ambiente virtual (muy pesado) |
| `build/` | ❌ NO | Compilación temporal |
| `dist/` | ❌ NO | Solo .exe antiguo |
| `__pycache__/` | ❌ NO | Caché de Python |
| `.git/` | ❌ NO | Histórico git (opcional) |

---

## 🔧 Tamaño Estimado

| Elemento | Tamaño |
|----------|--------|
| Código + docs | ~500 KB |
| `venv/` (con todo) | 500+ MB |
| `dist/AGENTE_FINAL.exe` | ~50 MB |

**Total sin venv:** ~60 MB  
**Total con venv:** ~600+ MB

---

## 🚀 Opción Alternativa: Script de Setup

Crear `setup.bat` para que la otra PC lo ejecute automáticamente:

```batch
@echo off
echo Creando ambiente virtual...
python -m venv venv

echo Activando ambiente...
call venv\Scripts\activate

echo Instalando dependencias...
pip install -r requeriments.txt

echo Regenerando AGENTE_FINAL.exe...
pyinstaller AGENTE_FINAL.spec

echo.
echo ✅ Configuración completada!
echo Ahora puedes ejecutar: Iniciar_NOC.bat
pause
```

Guarda como `setup.bat` y comparte junto con el proyecto.

---

## 📋 Checklist antes de Compartir

- [ ] Comprimir sin `venv/`, `build/`, `dist/`, `__pycache__/`
- [ ] Incluir `requeriments.txt`
- [ ] Incluir `AGENTE_FINAL.spec`
- [ ] Incluir `setup.bat` (opcional pero recomendado)
- [ ] Verificar que `.gitignore` está presente
- [ ] Prueba en otra PC antes de entregar

---

## 🆘 Si Algo Falla en la Otra PC

**Error: `venv\Scripts\python.exe no existe`**
- Ejecutar `python -m venv venv`
- Ejecutar `pip install -r requeriments.txt`

**Error: `ModuleNotFoundError`**
- Verificar que está activado el venv
- Reinstalar: `pip install -r requeriments.txt --force-reinstall`

**Error: `AGENTE_FINAL.exe no existe`**
- Instalar PyInstaller: `pip install pyinstaller`
- Regenerar: `pyinstaller AGENTE_FINAL.spec`

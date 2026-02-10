# 📘 Guía de Despliegue y Solución de Problemas

## 🚀 Opción Rápida: Solo Agentes (Para Monitorear)
Esta guía explica cómo instalar el sistema en una nueva PC, cómo distribuir agentes y cómo solucionar los problemas de conexión más comunes.

Si solo quieres **monitorear otras PCs** (no desarrollar en ellas), no necesitas copiar todo el proyecto. Sigue este flujo "Universal":
---

### 1. Configurar en tu Servidor (Una sola vez)
1. Abre `src/config.py`.
2. Busca `CONFIGURACION_PREDETERMINADA`.
3. Cambia `"ip": "127.0.0.1"` por la **IP Real de tu Servidor** (ej: `192.168.1.50`).
## 🏆 Reglas de Oro (Lee esto primero)

### 2. Generar el Ejecutable
Ejecuta en tu terminal:
```powershell
pyinstaller AGENTE_FINAL.spec
```
1. **Si cambias la IP en el código:** Debes **BORRAR** el archivo `config/config.json` para que el sistema tome el cambio. Si no lo borras, seguirá usando la configuración vieja.
2. **Si hay "Timeout":** Casi siempre es el Firewall de Windows. Ejecuta el comando de desbloqueo (ver abajo).
3. **Para instalar rápido:** Usa siempre `setup.bat` en lugar de hacerlo manual.

### 3. Distribuir
1. Ve a la carpeta `dist/`.
2. Copia el archivo `AGENTE_FINAL.exe`.
3. Pégalo en cualquier PC de tu red (PC2, PC3, PC4...).
4. **¡Listo!** Al abrirlo, se conectará automáticamente a tu servidor.

---

## 📦 Opción Completa: Mover el Proyecto (Para Desarrollo)
## 🚀 Escenario A: Instalar Servidor Completo (Nueva PC)
*Usa esto si quieres mover todo el sistema (Dashboard + API) a otra computadora.*

Usa esta opción si quieres mover todo el código fuente a otra PC para seguir programando.
1. **Copiar:** Copia toda la carpeta del proyecto (excepto `venv`, `build`, `dist`) a la nueva PC.
2. **Instalar:** Ejecuta `setup.bat`.
   - Esto instalará Python (si falta), creará el entorno virtual y descargará las librerías.
3. **Iniciar:** Ejecuta `Iniciar_NOC.bat`.

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
## 📡 Escenario B: Solo Agente (Monitorear PC Remota)
*Usa esto para monitorear otras computadoras sin instalar todo el proyecto en ellas.*

### 1. Preparar tu PC
### 1. Configurar IP (En tu PC Principal)
1. Abre `src/config.py`.
2. Edita `CONFIGURACION_PREDETERMINADA` > `servidor_central` > `"ip"`.
3. Pon la **IP de tu PC Principal** (ej: `192.168.4.142`).

**Comprimir sin las carpetas innecesarias:**
### 2. Generar Ejecutable
Ejecuta en tu terminal:
```powershell
# Opción A: Usando 7-Zip/WinRAR
# Click derecho → Agregar al archivo
# Marcar "Excluir carpetas": venv/, build/, dist/, __pycache__/, .git/

# Opción B: Comando PowerShell
Compress-Archive -Path . -DestinationPath Monitor_Servidores.zip -Exclude @("venv", "build", "dist", "__pycache__", ".git")
.\venv\Scripts\pyinstaller AGENTE_FINAL.spec
```

### 2. En la Otra PC
### 3. Distribuir
1. Copia `dist/AGENTE_FINAL.exe` a la PC remota.
2. **Importante:** Si ya había una versión anterior, borra el archivo `config.json` o la carpeta `config` en la PC remota.
3. Ejecuta el `.exe`.

**Paso 1: Extraer archivo**
```powershell
Extract-Archive Monitor_Servidores.zip
cd Monitor_Servidores
```

**Paso 2: Crear nuevo venv**
```powershell
python -m venv venv
venv\Scripts\activate
```

**Paso 3: Instalar dependencias**
```powershell
pip install -r requirements.txt
```

**Paso 4: Ejecutar**
```powershell
# Opción A: Doble clic en Iniciar_NOC.bat
Iniciar_NOC.bat

# Opción B: Regenerar AGENTE_FINAL.exe
pyinstaller AGENTE_FINAL.spec
```

---

## 📊 Archivos a Compartir
## 🔧 Solución de Problemas (Troubleshooting)

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
### 1. El Agente sigue conectando a la IP vieja
**Causa:** El agente tiene "memoria" (el archivo `config.json` guardado).
**Solución:**
1. Cierra el agente.
2. Ve a la carpeta `config` (o junto al .exe).
3. **Borra el archivo `config.json`**.
4. Vuelve a abrir el agente.

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
### 2. Error "Timeout" o "Sin conexión"
**Causa:** El Firewall de Windows en el Servidor está bloqueando la entrada.
**Solución:**
En la PC Servidor, abre **PowerShell como Administrador** y ejecuta:
```powershell
New-NetFirewallRule -DisplayName "NOC Monitor" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

Guarda como `setup.bat` y comparte junto con el proyecto.
### 3. Error "Host de destino inaccesible"
**Causa:** Las computadoras están en redes diferentes (ej. `.1.x` y `.4.x`) y no hay ruta entre ellas.
**Solución:**
- Opción A: Conectar ambas a la misma red WiFi/VPN.
- Opción B: Instalar **Tailscale** en ambas y usar la IP de Tailscale.

---

## 📋 Checklist antes de Compartir
## 📂 Qué compartir y qué no

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
| Carpeta | Acción | Por qué |
|---------|--------|---------|
| `src/` | ✅ Copiar | Es el código fuente. |
| `setup.bat` | ✅ Copiar | Instala todo automáticamente. |
| `venv/` | ❌ NO Copiar | Se rompe al moverlo. `setup.bat` creará uno nuevo. |
| `config/` | ⚠️ Cuidado | Contiene tu configuración local. Mejor borrar `config.json` al copiar. |

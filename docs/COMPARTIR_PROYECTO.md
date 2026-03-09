# Guía de Despliegue y Distribución

Este documento describe los procedimientos estándar para distribuir la aplicación de monitoreo a través de varios entornos, garantizando configuraciones de implementación estables.

## Escenario A: Despliegue de Agentes (Monitoreo de Nodos Remotos)
*Siga este procedimiento para desplegar el agente de seguimiento a las máquinas objetivo sin transferir todo el repositorio.*

### 1. Configure el Objetivo Central
1. Acceda al Servidor Central y abra `config/config.json`.
2. Localice el bloque `servidor_central`.
3. Actualice el campo `ip` para reflejar la dirección IP fija de su Servidor Central (ej. `"ip": "192.168.1.50"`).

### 2. Compile el Ejecutable del Agente
1. Ejecute `herramientas.bat` en el Servidor Central.
2. Seleccione la opción **[1] Compilar Agentes**.
3. Espere a que se complete el proceso de construcción de PyInstaller. La salida se ubicará en el directorio `dist/`.

### 3. Distribuya a los Nodos Objetivo
1. Navegue al directorio `dist/`.
2. Transfiera el ejecutable (`NOC_SERVICIO.exe`) y el script de instalación (`instalar_agente.bat`) al nodo objetivo.
3. En el nodo objetivo, ejecute `instalar_agente.bat` con **privilegios de Administrador**.
4. El agente se inicializará como un servicio en segundo plano y comenzará la transmisión de métricas.

*Nota: Si está actualizando una implementación de agente existente, debe eliminar el antiguo `config/config.json` en la máquina objetivo para forzarla a adoptar la nueva ruta de IP compilada.*

---

## Escenario B: Migración del Sistema Completo (Desarrollo/Configuración NOC)
*Siga este procedimiento para migrar todo el código fuente, incluyendo la API y el Dashboard, a una nueva máquina administrativa.*

### 1. Transferencia de Código
1. Comprima el directorio del proyecto.
   - **Crucial:** Excluya los siguientes directorios para evitar corrupción del entorno y reducir el tamaño de la carga útil:
     - `venv/` (Entorno virtual de Python)
     - `build/` (Artefactos de compilación)
     - `dist/` (Ejecutables compilados)
     - `__pycache__/` (Caché de bytecode de Python)
     - `.git/` (Historial de control de versiones)
2. Transfiera el archivo comprimido al nuevo Servidor Central.

### 2. Inicialización del Entorno
1. Extraiga el archivo.
2. Ejecute `setup.bat`. Este script:
   - Detectará o instalará Python.
   - Generará un nuevo entorno virtual (`venv`).
   - Instalará las dependencias requeridas desde `requirements.txt`.
   - Compilará los ejecutables locales.

### 3. Inicialización del Servicio
1. Ejecute `Iniciar_NOC.bat` para lanzar los servicios de API y Dashboard.

---

## Solución de Problemas de Conectividad

### 1. El Agente Reporta IP Heredada
**Síntoma:** El agente continúa intentando conectarse a una IP del Servidor Central obsoleta.
**Resolución:**
1. Termine el proceso del agente.
2. Localice el directorio `config/` adyacente al ejecutable.
3. Elimine el archivo `config.json`.
4. Reinicie el agente para regenerar la configuración basándose en los valores predeterminados compilados.

### 2. Tiempo de Espera Agotado / Conexión Rechazada
**Síntoma:** Los registros del agente indican un tiempo de espera agotado; el Servidor Central es inalcanzable.
**Resolución:**
Es probable que el Firewall de Windows en el Servidor Central esté restringiendo el tráfico entrante en el puerto designado.
1. Abra PowerShell como Administrador en el Servidor Central.
2. Ejecute el comando de configuración del firewall:
   ```powershell
   New-NetFirewallRule -DisplayName "Monitor NOC" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
   ```

### 3. Host de Destino Inalcanzable
**Síntoma:** Partición de red entre el Agente y el Servidor Central (ej. subredes dispares).
**Resolución:**
Asegúrese de que exista un enrutamiento adecuado entre los nodos. Implemente una solución VPN (ej. Tailscale o WireGuard) para establecer una red superpuesta plana si el enrutamiento físico no está disponible.

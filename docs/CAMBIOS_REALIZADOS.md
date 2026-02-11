# 📝 Registro de Cambios (Changelog)

## 📝 Código Python - Comentarios Añadidos

### `src/agente.py`
- Docstring resumido en cabecera
- Comentarios en línea para variables clave
- Docstrings en funciones

### `src/servidor.py`
- Docstring resumido en cabecera
- Comentarios en modelo Metricas
- Docstrings en endpoints

### `src/dashboard.py`
- Docstring resumido en cabecera
- Comentarios claros en estructura
- Docstring en función obtener_datos()

### `src/config.py`
- Definición de ruta para base de datos SQLite (`data/metricas.db`)

---

## 💾 Persistencia y Visualización (Nuevo)

### Base de Datos SQLite
- Reemplazo del almacenamiento volátil (RAM) por persistente (`metricas.db`).
- Historial de métricas conservado tras reinicios.
- Nuevo endpoint `/historial/{id}` en la API para consultar datos pasados.

### Gráficos Históricos
- Dashboard ahora muestra la evolución de la CPU en el tiempo.
- Uso de `pandas` para procesar series temporales.

---

## � Scripts Batch Creados

### `setup.bat` (Nuevo)
- Detecta si Python está instalado
- Crea venv automáticamente
- Instala todas las dependencias
- Regenera AGENTE_FINAL.exe
- **Primera cosa que debe ejecutar el usuario**

---

## �📚 Documentación Markdown

### 1. **README.md** (Actualizado)
   - Ahora menciona `setup.bat` para primera instalación
   - Enfoque en ejecutables (.bat y .exe)
   - Link a COMPARTIR_PROYECTO.md

### 2. **docs/instalacion.md**
   - Opción A: Ejecutables (recomendado)
   - Opción B: Manual con comandos
   - Tabla troubleshooting

### 3. **docs/COMPONENTES.md**
   - Sección de ejecutables (.bat y .exe)
   - Cómo regenerar .exe
   - Componentes de código explicados

### 4. **docs/arquitectura.md**
   - Diagrama ASCII flujo
   - Protocolo HTTP detallado
   - Limitaciones y seguridad

### 5. **docs/REFERENCIA_RAPIDA.md**
   - Ejecución con doble clic
   - Configuración de IP_CENTRAL
   - Troubleshooting rápido

### 6. **docs/COMPARTIR_PROYECTO.md** (Creado)
   - Problemas potenciales al compartir
   - Qué carpetas NO incluir (venv, build, dist)
   - Paso a paso para otra PC
   - **Nueva sección:** Guía para distribuir solo el Agente (.exe)
   - Menciona setup.bat

## 🚀 Actualización: Control y Seguridad (Nuevo)

### 🔄 Gestión Remota
- **Botón de Reinicio:** Implementado en Dashboard con confirmación de seguridad (¿Estás seguro?).
- **Cola de Comandos:** El servidor gestiona órdenes pendientes y las entrega al agente cuando este reporta.

### 🔒 Seguridad y Red
- **Soporte SSL/TLS:** Configuración centralizada para certificados `.pem` y `.key` (HTTPS).
- **Alertas por Email:** Integración SMTP para notificar caídas de servidores.
- **Monitor de Latidos (Heartbeat):** Detección automática de agentes desconectados (>5 min sin reportar).

### ⚠️ Pendiente / Por Implementar
- **Lógica en Agente:** El servidor envía el comando `"reiniciar"`, pero falta verificar que `agente.py` tenga la lógica para recibirlo y ejecutar `subprocess.run("shutdown /r")`.
- **Configuración SMTP:** El archivo `config.json` debe actualizarse con credenciales reales para que funcionen los correos.

---

## 🎯 Resultado Final

✅ Sistema listo para ejecutarse con .bat y .exe  
✅ Documentación enfocada en usuarios finales  
✅ Comentarios resumidos en código  
✅ Guía completa para instalación y uso  

**Última actualización:** Enero 2026

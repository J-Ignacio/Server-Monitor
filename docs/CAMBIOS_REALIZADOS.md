# Registro de Cambios

## Refactorización del Código Base y Documentación

### Estandarización de Módulos Python
- `src/agente.py`: Se implementaron docstrings completos estilo Google, se refinaron los comentarios en línea para mayor claridad y se estableció un tono técnico profesional.
- `src/config.py`: Se centralizó la lógica de configuración con docstrings detallados, asegurando definiciones claras de propiedades y documentación robusta sobre el manejo de errores.
- `src/servidor.py`: Se actualizaron los encabezados de los módulos y los docstrings de los endpoints para reflejar los estándares de la API REST.
- `src/dashboard.py`: Se estructuró la lógica de visualización con documentación modular clara.

---

## Persistencia y Análisis de Datos

### Integración con SQLite
- Transición de un almacenamiento de métricas volátil en memoria a una arquitectura SQLite persistente (`data/metricas.db`).
- Se introdujo la retención de datos históricos, sobreviviendo a reinicios del sistema.
- Se implementó un nuevo endpoint de API, `/historial/{id}`, para facilitar las consultas de series temporales.

### Recolección de Métricas Ampliada
- **Uso de Disco:** Se integró lógica para capturar el porcentaje de uso de la partición principal (`C:` o `/`).
- **Migración del Esquema de Base de Datos:** Se implementaron actualizaciones automáticas de esquema, permitiendo que el servidor añada dinámicamente la columna `disk` a bases de datos heredadas.
- **Gráficos Históricos:** Se mejoró el Dashboard para renderizar gráficos dinámicos de líneas de series temporales para el uso de CPU a lo largo del tiempo a través de la biblioteca `pandas`.

---

## Automatización y Herramientas

### Automatización de la Inicialización del Sistema
- **`setup.bat`:** Se creó un script de inicio completo que automatiza la preparación del entorno:
  - Valida las instalaciones de Python.
  - Aprovisiona el entorno virtual (`venv`).
  - Resuelve las dependencias vía `pip`.
  - Compila los artefactos ejecutables necesarios (variantes Portable y de Servicio).

---

## Documentación de Arquitectura Mejorada

### Revisión de `/docs`
- **`instalacion.md`:** Se estandarizaron las instrucciones de implementación para entornos automatizados y basados en código fuente.
- **`COMPONENTES.md`:** Arquitectura detallada del sistema, responsabilidades de los componentes y estructuras de configuración.
- **`arquitectura.md`:** Se refinaron los diagramas de flujo de datos y las definiciones de protocolos para revisión técnica avanzada.
- **`COMPARTIR_PROYECTO.md`:** Se establecieron protocolos claros para la distribución del sistema y los escenarios de implementación de agentes.
- **`REFERENCIA_RAPIDA.md`:** Se consolidó una hoja de referencia técnica para operaciones rápidas.

---

## Gestión Remota y Seguridad

### Capacidades de Ejecución Remota
- **Operaciones de Reinicio:** Se implementaron controles administrativos dentro del Dashboard para poner en cola comandos de reinicio remotos.
- **Sondeo de Comandos:** Se mejoró la API para gestionar colas de instrucciones, enviando comandos a los agentes durante los intercambios estándar de cargas útiles de métricas.
- **Integración de Agentes:** `agente.py` analiza con éxito las instrucciones de reinicio y ejecuta protocolos `shutdown` a nivel de sistema operativo.

### Mejoras en Redes y Confiabilidad
- **Infraestructura SSL/TLS:** Se agregó andamiaje de configuración para la comunicación HTTPS basada en certificados.
- **Alertas SMTP:** Se construyó una integración fundamental para las notificaciones de fallas de nodos basadas en correo electrónico.
- **Monitoreo de Latidos (Heartbeat):** Se integró lógica para marcar a los agentes que no transmiten telemetría dentro de un umbral de 5 minutos.

### Elementos Diferidos
- Validar y habilitar la configuración SMTP dentro de `config.json` para entornos de producción.

---

**Última Actualización:** Enero 2026

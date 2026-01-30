# 🗺️ Hoja de Ruta (Roadmap)

Ideas y mejoras planificadas para futuras versiones del Monitor NOC.

## 🚀 Próximas Mejoras (Corto Plazo)

- [x] **Soporte de Temperatura:** Investigar librerías (`OpenHardwareMonitor` o WMI) para leer temperatura de CPU en Windows.
- [ ] **Alertas Sonoras:** Reproducir un sonido en el Dashboard cuando la CPU supere el 90%.
- [x] **Modo Oscuro/Claro:** Toggle en el Dashboard.
- [🚧] **Modo Oscuro/Claro:** Toggle en el Dashboard (En curso).

## 🛠️ Mejoras Técnicas (Mediano Plazo)

- [ ] **Base de Datos Real:** Migrar de memoria RAM a SQLite para guardar historial de métricas.
- [ ] **Gráficos Históricos:** Mostrar la evolución de CPU/RAM en la última hora (requiere BD).
- [ ] **Autenticación:** Login simple (Usuario/Pass) para acceder al Dashboard.

## 🔮 Futuro (Largo Plazo)

- [ ] **Agente Linux:** Adaptar `agente.py` para funcionar en servidores Linux/Ubuntu.
- [ ] **Notificaciones Email/Telegram:** Enviar alerta si un servidor se desconecta.
- [ ] **HTTPS:** Cifrar la comunicación entre agentes y servidor.

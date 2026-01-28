# ⚡ Referencia Rápida (Cheat Sheet)

## Ejecución (Lo Más Importante)

### Central
```bash
# Doble clic en:
Iniciar_NOC.bat
```
Se abre API y Dashboard automáticamente.

### Servidor Remoto
```bash
# Doble clic en:
AGENTE_FINAL.exe
```
O ejecutar `config.bat` si necesitas configurar IP_CENTRAL.

---

## Configuración Crítica

**En `config.bat` del servidor (o editar agente.py línea 8):**
```batch
set IP_CENTRAL=192.168.4.143  # ← Cambiar con tu IP de laptop
```

---

## URLs Importantes

| URL | Descripción |
|-----|-------------|
| `http://localhost:8501` | Dashboard Streamlit |
| `http://localhost:8000/estado` | API GET últimas métricas (JSON) |
| `http://localhost:8000/docs` | API documentación automática |

---

## Estructura de Datos Retornada

**GET /estado retorna:**
```json
{
  "SERVIDOR1 (192.168.1.100)": {
    "cpu": 45.2,
    "ram": 62.1,
    "temp": 0.0
  },
  "SERVIDOR2 (192.168.1.101)": {
    "cpu": 28.5,
    "ram": 41.3,
    "temp": 0.0
  }
}
```

---

## Archivos Ejecutables

| Archivo | Uso |
|---------|-----|
| `Iniciar_NOC.bat` | Ejecutar central (API + Dashboard) |
| `AGENTE_FINAL.exe` | Ejecutar en servidores remotos |
| `config.bat` | Configurar agente (crear en servidor) |

---

## Ciclo de Ejecución

1. **Agente** (cada 5s): recopila CPU/RAM → POST /reportar
2. **Servidor**: almacena en memoria
3. **Dashboard** (cada 2s): GET /estado → visualiza

---

## Troubleshooting Rápido

| Error | Causa | Solución |
|-------|-------|----------|
| Dashboard vacío | Agente no conecta | Verificar IP_CENTRAL |
| "Port 8000 in use" | Proceso anterior no cerrado | Reiniciar laptop |
| Agente no inicia | Archivo .exe corrupto | Regenerar con PyInstaller |
| Conexión rechazada | Firewall bloquea puerto | `netsh advfirewall firewall add rule...` |

---

## Comandos Desarrollo (Si necesitas)

```bash
# Ver IP local
ipconfig

# Verificar puerto 8000
netstat -ano | findstr :8000

# Regenerar AGENTE_FINAL.exe
pyinstaller AGENTE_FINAL.spec

# Instalar dependencias
pip install -r requeriments.txt
```

# 🛠️ Guía de Instalación

## Configuración de la Central (Laptop)
1. Instalar dependencias: `pip install -r requeriments.txt`.
2. **Firewall**: Abrir puerto **8000** (Entrada) para permitir reportes de red.
3. Iniciar Servidor: `python servidor.py`
4. Iniciar Dashboard: `streamlit run dashboard.py`

## Configuración del Agente (Servidor Remoto)
1. Copiar `agente.py`.
2. Modificar la variable `IP_CENTRAL` con la IP de la laptop.
3. Ejecutar: `python agente.py`
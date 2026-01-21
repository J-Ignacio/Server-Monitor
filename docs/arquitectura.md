# 📡 Arquitectura de Red y Despliegue

El sistema opera íntegramente a través de la **Red Local (LAN)** de la empresa.

## 🔗 Comunicación de Datos
- **Protocolo**: HTTP (JSON).
- **Puerto Central**: 8000.
- **Flujo**: El Agente envía datos a la IP privada de la Laptop Central mediante solicitudes POST.

## 🛠️ Método de Despliegue (Paso a Paso)
Para instalar el monitoreo en los servidores sin necesidad de acceso físico:
1. **Acceso Remoto**: Se utiliza **Escritorio Remoto de Windows (RDP)** para entrar a los servidores usando su IP local.
2. **Transferencia de Código**: Se realiza mediante **Copiar y Pegar** el archivo `agente.py` directamente desde la PC local hacia la ventana del Escritorio Remoto.
3. **Ejecución**: Se abre la terminal dentro del servidor remoto para lanzar el script.
"""
Wrapper para ejecutar el Agente como Servicio de Windows.
Requiere permisos de Administrador para instalarse.
"""
import win32serviceutil
import win32service
import win32event
import servicemanager
import sys
import threading
from pathlib import Path

# Asegurar que podemos importar el módulo 'agente' desde el mismo directorio
base_path = Path(__file__).resolve().parent
sys.path.append(str(base_path))

from agente import enviar_datos


class AgenteService(win32serviceutil.ServiceFramework):
    _svc_name_ = "NOCMonitorAgente"
    _svc_display_name_ = "NOC Monitor Agente"
    _svc_description_ = "Envía métricas de CPU/RAM/Disco al servidor central NOC."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.stop_event = threading.Event()

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.stop_event.set()

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )

        try:
            enviar_datos(stop_event=self.stop_event)
        except Exception as e:
            servicemanager.LogErrorMsg(f"Error fatal en agente: {e}")


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AgenteService)

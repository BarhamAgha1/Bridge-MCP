"""
Bridge MCP - Windows Service Installer
======================================
Installs local_agent.py as a background Windows service.

Usage:
  python install_service.py install
  python install_service.py start
  python install_service.py stop
  python install_service.py remove
"""

import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
import asyncio
from pathlib import Path

# Service configuration
SERVICE_NAME = "BridgeMCPLocalAgent"
SERVICE_DISPLAY_NAME = "Bridge MCP Agent"
SERVICE_DESCRIPTION = "Allows AI to control this PC via Bridge MCP."

# Import local agent to run it
sys.path.insert(0, str(Path(__file__).parent))
import local_agent

class AppServerSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = SERVICE_NAME
    _svc_display_name_ = SERVICE_DISPLAY_NAME
    _svc_description_ = SERVICE_DESCRIPTION

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        # Stop the local agent
        # (This is a simplified stop, in a real scenario we'd signal the loop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,''))
        self.main()

    def main(self):
        # Run the local agent's main loop
        # We need to run it in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Auto-register first
        loop.run_until_complete(local_agent.auto_register_with_bridge())
        
        # Start the server (simplified for service wrapper)
        # Note: In a real production service, we'd want more robust process management
        # For now, we'll import and run main, but we need to handle the loop correctly
        try:
             loop.run_until_complete(local_agent.main())
        except Exception as e:
            servicemanager.LogErrorMsg(str(e))

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(AppServerSvc)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(AppServerSvc)

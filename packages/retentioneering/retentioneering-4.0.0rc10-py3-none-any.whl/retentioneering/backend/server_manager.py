from __future__ import annotations

from typing import Any, Dict, Optional

from IPython.core.display import display

from retentioneering.backend import JupyterServer
from retentioneering.exceptions.server import ServerErrorWithResponse
from retentioneering.utils.singleton import Singleton

from .event_bridge import EventBridge


class ServerManager:
    __metaclass__ = Singleton

    def __init__(self) -> None:
        self._servers: Dict[str, JupyterServer] = {}
        self._bridge: Optional[EventBridge] = None
        self._listener_created = False

        self._create_main_listener()
        display(self._bridge)

    def _find_server(self, server_id: str) -> JupyterServer | None:
        return self._servers.get(server_id)

    def _on_bridge_message(self, content: Dict[str, Any]) -> None:
        if self._bridge is None:
            return

        server_id = content.get("server_id")
        request_id = content.get("request_id")
        request_type = content.get("request_type")
        method = content.get("method")
        payload = content.get("payload", {})

        if server_id is None or request_id is None or (request_type != "handshake" and method is None):
            self._bridge.send(
                {
                    "success": False,
                    "server_id": server_id,
                    "request_id": request_id,
                    "method": method,
                    "result": "InvalidRequest",
                }
            )
            return

        # handshake
        if request_type == "handshake":
            self._bridge.send(
                {
                    "success": True,
                    "server_id": server_id,
                    "request_id": request_id,
                    "request_type": "handshake",
                }
            )
            return

        if method is None:
            return

        server = self._find_server(server_id)

        if server is None:
            self._bridge.send(
                {
                    "success": False,
                    "server_id": server_id,
                    "request_id": request_id,
                    "method": method,
                    "result": "ServerNotFound",
                }
            )
            return

        try:
            result = server.dispatch_method(method=method, payload=payload)
            self._bridge.send(
                {
                    "success": True,
                    "server_id": server_id,
                    "request_id": request_id,
                    "method": method,
                    "result": result,
                }
            )
        except ServerErrorWithResponse as err:
            self._bridge.send(
                {
                    "success": False,
                    "server_id": server_id,
                    "request_id": request_id,
                    "method": method,
                    "result": err.dict(),
                }
            )
        except Exception as err:
            wrapped = ServerErrorWithResponse(message=str(err), type="unexpected_error")
            self._bridge.send(
                {
                    "success": False,
                    "server_id": server_id,
                    "request_id": request_id,
                    "method": method,
                    "result": wrapped.dict(),
                }
            )

    def _create_main_listener(self) -> None:
        if self._listener_created:
            return
        bridge = EventBridge()

        def _recv(_: Any, content: Dict[str, Any], buffers: Any) -> None:
            self._on_bridge_message(content)

        bridge.on_msg(_recv)
        self._bridge = bridge
        self._listener_created = True

    def create_server(self, pk: Optional[str] = None) -> JupyterServer:
        server = JupyterServer(pk=pk, bridge=self._bridge)
        self._servers[server.pk] = server
        return server

    @property
    def widget(self) -> EventBridge | None:
        return self._bridge

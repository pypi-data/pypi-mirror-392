from __future__ import annotations

import uuid
from typing import Any, Callable, Optional, Dict

import ipywidgets as widgets
from traitlets import Unicode

from retentioneering.exceptions.server import ServerNotFoundActionError, ServerErrorWithResponse
from retentioneering.utils.singleton import Singleton
from .event_bridge import EventBridge


class Action:
    def __init__(self, method: str, callback: Callable):
        self.method = method
        self.callback = callback


class JupyterServer:
    def __init__(self, pk: Optional[str] = None, bridge: Optional[EventBridge] = None):
        self.pk = pk or self._make_id()
        self.actions: Dict[str, Action] = {}
        self._bridge = bridge

    def _make_id(self) -> str:
        return str(uuid.uuid4())

    def register_action(self, method: str, callback: Callable) -> None:
        self.actions[method] = Action(method, callback)

    def _find_action(self, method: str) -> Action | None:
        return self.actions.get(method)

    def dispatch_method(self, method: str, payload: dict) -> Any:
        action = self._find_action(method)
        if action is not None:
            return action.callback(payload)
        raise ServerNotFoundActionError("method not found!", method=method)
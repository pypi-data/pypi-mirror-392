# event_bridge.py
from __future__ import annotations

import anywidget
import traitlets as T


class EventBridge(anywidget.AnyWidget):
    bridge_id = T.Unicode().tag(sync=True)

    _esm = r"""
    export function render({ model, el }) {
      const id = model.get("bridge_id") || (model.model_id || "");

      const g = globalThis;
      g.IpyBridge = g.IpyBridge ?? {};

      const listeners = new Set();

      g.IpyBridge[id] = {
        send: (payload) => { model.send(payload); },
        subscribe: (handler) => {
          if (typeof handler === "function") {
            listeners.add(handler);
            return () => listeners.delete(handler);
          }
          return () => {};
        }
      };

      model.on("msg:custom", (content) => {
        for (const h of Array.from(listeners)) {
          try { h(content); } catch (e) { console.error(e); }
        }
      });

      el.style.display = "none";
    }
    """

    def __init__(self, **kwargs: dict) -> None:
        super().__init__(**kwargs)
        real_id = getattr(self, "model_id", "") or getattr(self, "_model_id", "") or ""
        self.bridge_id = real_id

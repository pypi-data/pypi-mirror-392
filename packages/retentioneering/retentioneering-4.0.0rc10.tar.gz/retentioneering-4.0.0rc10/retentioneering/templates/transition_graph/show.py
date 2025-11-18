from __future__ import annotations

import json
from typing import Any

from jinja2 import Environment, PackageLoader, Template

from retentioneering.backend import JupyterServer


class TransitionGraphRenderer:
    _template: Template
    _env: Environment

    def __init__(self) -> None:
        self._env = Environment(
            loader=PackageLoader(package_name="retentioneering", package_path="templates"),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self._template = self._env.get_template("transition_graph/template.html")

    def show(
        self,
        *,
        script_url: str,
        style: str,
        state: dict | str,
        server: JupyterServer,
        bridge_model_id: str,
        id: str,
        title: str | None = None,
    ) -> str:
        if isinstance(state, dict):
            state_json = json.dumps(state, ensure_ascii=False)
        else:
            state_json = state

        return self._template.render(
            id=id,
            style=style,
            state=state_json,
            script_url=script_url,
            bridge_id=bridge_model_id,
            server_id=server.pk,
            title=title or "Retentioneering Transition Graph Application",
        )

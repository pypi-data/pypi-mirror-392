import anywidget
import traitlets
from ipywidgets import DOMWidget
from ._version import __eox_map_version__

map_esm = f"""
import \"https://cdn.jsdelivr.net/npm/@eox/map@{__eox_map_version__}/dist/eox-map.js\";

export function render(view) {{
  const map = document.createElement(\"eox-map\");
  map.style.width = view.model.get(\"layout\").width;
  map.style.height = view.model.get(\"layout\").height || \"100%\";
  map.layers = view.model.get(\"layers\");
  map.id = view.model.get(\"element_id\");
  view.model.on(\"change:layers\", () => {{ map.layers = view.model.get(\"layers\"); }});
  view.model.on(\"change:element_id\", () => {{ map.id = view.model.get(\"element_id\"); }});
  view.el.appendChild(map);
}}
"""

class EOxMap(anywidget.AnyWidget, DOMWidget):
    _esm = map_esm
    layers = traitlets.List([]).tag(sync=True)
    element_id = traitlets.Unicode("").tag(sync=True)
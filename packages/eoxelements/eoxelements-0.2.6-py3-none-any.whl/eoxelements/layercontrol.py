import anywidget
import traitlets
from ipywidgets import DOMWidget
from ._version import __eox_layercontrol_version__

layercontrol_esm = f"""
import \"https://cdn.jsdelivr.net/npm/@eox/layercontrol@{__eox_layercontrol_version__}/dist/eox-layercontrol.js\";

export function render(view) {{
  const control = document.createElement(\"eox-layercontrol\");
  control.style.width = view.model.get(\"layout\").width;
  control.style.height = view.model.get(\"layout\").height;
  control.for = view.model.get(\"for_id\");
  view.model.on(\"change:for_id\", () => {{ control.for = view.model.get(\"for_id\"); }});
  view.el.appendChild(control);
}}
"""

class EOxLayerControl(anywidget.AnyWidget, DOMWidget):
    _esm = layercontrol_esm
    for_id = traitlets.Unicode("").tag(sync=True)
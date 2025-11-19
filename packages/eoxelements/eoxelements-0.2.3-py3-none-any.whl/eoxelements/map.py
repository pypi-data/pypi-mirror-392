import anywidget
import traitlets
from ipywidgets import DOMWidget
from ._version import __eox_map_version__

map_esm = f"""
import \"https://cdn.jsdelivr.net/npm/@eox/map@{__eox_map_version__}/dist/eox-map-advanced-layers-and-sources.js\";
import \"https://cdn.jsdelivr.net/npm/@eox/map@{__eox_map_version__}/dist/eox-map.js\";

export function render(view) {{
  const map = document.createElement("eox-map");
  map.style.width = view.model.get("layout").width;
  map.style.height = view.model.get("layout").height || "100%";
  map.id = view.model.get("element_id");
  map.zoom = view.model.get("zoom");
  map.center = view.model.get("center");
  map.config = view.model.get("config");
  map.projection = view.model.get("projection");
  map.preventScroll = view.model.get("prevent_scroll");
  view.model.on("change:config", () => { map.config = view.model.get("config"); });
  view.model.on("change:layers", () => { map.layers = view.model.get("layers"); });
  view.model.on("change:element_id", () => { map.id = view.model.get("element_id"); });
  view.model.on("change:zoom", () => { map.zoom = view.model.get("zoom"); });
  view.model.on("change:center", () => { map.center = view.model.get("center"); });
  view.model.on("change:config", () => { map.config = view.model.get("config"); });
  view.model.on("change:projection", () => { map.projection = view.model.get("projection"); });
  view.model.on("change:prevent_scroll", () => { map.preventScroll = view.model.get("prevent_scroll"); });
  view.el.appendChild(map);
}}
"""

class EOxMap(anywidget.AnyWidget, DOMWidget):
    _esm = map_esm
    layers = traitlets.List([]).tag(sync=True)
    element_id = traitlets.Unicode("").tag(sync=True)
    zoom = traitlets.Int(0).tag(sync=True)
    center = traitlets.List([]).tag(sync=True)
    config = traitlets.Dict({}).tag(sync=True)
    projection = traitlets.Unicode("").tag(sync=True)
    prevent_scroll = traitlets.Bool(False).tag(sync=True)
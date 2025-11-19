import anywidget
import traitlets
from ipywidgets import DOMWidget
from ._version import __eox_chart_version__

chart_esm = f"""
import "https://cdn.jsdelivr.net/npm/@eox/chart@{__eox_chart_version__}/dist/eox-map-advanced-layers-and-sources.js";
import "https://cdn.jsdelivr.net/npm/@eox/chart@{__eox_chart_version__}/dist/eox-chart.js";

export function render(view) {{
  const chart = document.createElement("eox-chart");
  chart.style.width = view.model.get("layout").width;
  chart.style.height = view.model.get("layout").height || \"100%\";
  view.model.on("change:layout", () => {{
    chart.style.width = view.model.get("layout").width;
    chart.style.height = view.model.get("layout").height;
  }});
  chart.spec = view.model.get("spec");
  chart.dataValues = view.model.get("dataValues");
  chart.opt = view.model.get("opt");
  chart.noShadow = view.model.get("noShadow");
  view.model.on("change:spec", () => {{ chart.spec = view.model.get("spec"); }});
  view.model.on("change:dataValues", () => {{ chart.dataValues = view.model.get("dataValues"); }});
  view.model.on("change:opt", () => {{ chart.opt = view.model.get("opt"); }});
  view.model.on("change:noShadow", () => {{ chart.noShadow = view.model.get("noShadow"); }});
  chart.addEventListener("click:item", (e) => {{
    view.model.send({{ event: "click", item: e.detail.item }});
  }});
  chart.addEventListener("pointermove:item", (e) => {{
    view.model.send({{ event: "hover", item: e.detail.item }});
  }});
  view.el.appendChild(chart);
}}
"""

class EOxChart(anywidget.AnyWidget, DOMWidget):
    _esm = chart_esm
    spec = traitlets.Dict({}).tag(sync=True)
    dataValues = traitlets.Dict({}).tag(sync=True)
    opt = traitlets.Dict({}).tag(sync=True)
    noShadow = traitlets.Bool(False).tag(sync=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._click_handlers = []
        self._hover_handlers = []
        self.on_msg(self._handle_custom_msg)
        
    def _handle_custom_msg(self, msg, *args):
        event_type = msg.get("event")
        item = msg.get("item")
        if event_type == "click":
            for handler in self._click_handlers:
                handler(item)
        elif event_type == "hover":
            for handler in self._hover_handlers:
                handler(item)

    def on_click(self, callback):
        self._click_handlers.append(callback)

    def on_hover(self, callback):
        self._hover_handlers.append(callback)
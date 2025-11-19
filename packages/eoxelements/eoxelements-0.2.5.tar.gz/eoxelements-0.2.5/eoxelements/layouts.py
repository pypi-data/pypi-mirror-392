import uuid
from ipywidgets import HBox, Layout
from .map import EOxMap
from .layercontrol import EOxLayerControl

class EOxMapWithControl(HBox):
    """
    A convenience widget that displays an EOxMap and
    an EOxLayerControl side-by-side.
    """
    def __init__(self, layers=[], config=None, map_layout=None, control_layout=None, **kwargs):
        map_id = f"eox-map-{uuid.uuid4()}"
        if map_layout is None:
            map_layout = Layout(flex='1 1 70%', height='400px')
        if control_layout is None:
            control_layout = Layout(flex='1 1 30%', height='400px')
        self.map = EOxMap(
            config=config,
            layers=layers,
            element_id=map_id,
            layout=map_layout
        )
        self.control = EOxLayerControl(
            for_id=f"#{map_id}",
            layout=control_layout
        )
        super().__init__(children=[self.map, self.control], **kwargs)
    @property
    def layers(self):
        return self.map.layers
    @layers.setter
    def layers(self, value):
        self.map.layers = value
    @property
    def config(self):
        return self.map.config
    @config.setter
    def config(self, value):
        self.map.config = value

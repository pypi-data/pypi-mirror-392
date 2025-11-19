# EOxElements Jupyter

A minimal Python package for using EOxElements web components (eox-map, eox-layercontrol, etc.) inside Jupyter Notebooks. Inspired by ipyleaflet and ipyopenlayers, this package provides a simple API for inclduing EOxElements.

## Features
- Easy-to-use Python wrappers for EOxElements web components
- Version pinning for JS components via CDN
- Designed for use in Jupyter Notebooks

## Installation

```bash
pip install eoxelements
```

## Usage

```python
from eoxelements import EOxMapWithControl

# Define map layers
map_layers = [
    {
        "type": "Tile",
        "properties": {"id": "osm", "title": "OSM"},
        "source": {"type": "OSM"},
    }
]

# Create and display the widget
m = EOxMapWithControl(layers=map_layers)
display(m)
```

## Development & Release Automation
- JS component versions are pinned in `eoxelements/_version.py` and updated via CI/CD.
- Publishing to PyPI is automated using GitHub Actions (`.github/workflows/publish.yml`).

## License
MIT

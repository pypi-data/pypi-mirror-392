# Natal

> create Natal Chart with ease

## Features

- SVG natal chart generation in pure python
- composite chart (transit/synastry/sun return ... etc) generation
- highly configurable
    - all planets, asteroids, vertices can be enabled / disabled
    - orbs for each aspect
    - light, dark, or mono theme
    - light / dark theme color definitions
    - chart stroke, opacity, font, spacing between planets ...etc
- high precision astrological data with [Swiss Ephemeris]
- natal chart data statistics
    - element, modality, and polarity counts
    - planets in each houses
    - quadrant and hemisphere distribution
    - aspect pair counts
    - composite chart aspects
    - aspects cross reference table
    - generate report in markdown or html
- thoroughly tested with `pytest`

## Sample Charts

- default dark theme

<img src="https://raw.githubusercontent.com/hoishing/natal/refs/heads/main/docs/assets/chart_dark.png" width=600/>

- default light theme

<img src="https://raw.githubusercontent.com/hoishing/natal/refs/heads/main/docs/assets/chart_light.png" width=600/>

- mono theme

<img src="https://raw.githubusercontent.com/hoishing/natal/refs/heads/main/docs/assets/chart_mono.png" width=600/>

## Quick Start

- installation

`uv add natal`

- generate a chart

```python
from natal import Data, Chart

# create chart data object
mimi = Data(
    name="MiMi",
    utc_dt="1980-04-20 06:30",
    lat=25.0531,
    lon=121.526,
)

# return natal chart in SVG string
Chart(mimi, width=600).svg

# create transit data object
transit = Data(
    name="Transit",
    utc_dt="2024-01-01 05:30",
    lat=25.0531,
    lon=121.526,
)

# create a transit chart
transit_chart = Chart(
    data1=mimi, 
    data2=transit, 
    width=600
)

# view the composite chart in jupyter notebook
from IPython.display import HTML

HTML(transit_chart.svg)
```

following SVG chart will be produced:

<img src="https://raw.githubusercontent.com/hoishing/natal/refs/heads/main/docs/assets/composite_dark.png" width=600/>

- see [demo.ipynb] for the chart creation

## Data Object

```python
## -- retrieve natal chart properties -- ##

mimi.planets     # list[Planet]
mimi.houses      # list[House]
mimi.extras      # list[Extra]
mimi.vertices    # list[Vertex]
mimi.signs       # list[Sign]
mimi.aspects     # list[Aspect]
mimi.quadrants   # list[list[Aspectable]]

# Planet object 
sun = mimi.planets[0]

sun.degree # 30.33039116987769
sun.normalized_degree # 230.62043431588035 # degree relative to Asc
sun.color # fire
sun.speed # 0.9761994105153413
sun.retro # False
sun.dms # 00°19'
sun.signed_dms # 00°♉19'
sun.signed_deg # 0
sun.sign.name # taurus
sun.sign.symbol # ♉
sun.sign.value # 2
sun.sign.color # earth
sun.sign.ruler # venus
sun.sign.classic_ruler # venus
sun.sign.element # earth
sun.sign.modality # fixed
sun.sign.polarity # negative

# Aspect object
aspect = mimi.aspects[0]

aspect.body1 # sun Planet obj 
aspect.body2 # mars Planet obj
aspect.aspect_member # AspectMember(name='trine', symbol='△', value=120, color='air')
aspect.applying # False
aspect.orb # 3.3424
```

## Configuration

- create a `Config` object and assign it to `Data` object
- it will override the default settings in `config.py`
- a sample config as follow:

```py
from natal.config import Display, Config, Orb

# adjust which celestial bodies to display
display = Display(
    mc = False,
    asc_node = False,
    chiron = True
)

# adjust orbs for each aspect
orb = Orb(
    conjunction = 8,
    opposition = 8,
    trine = 6,
    square = 6,
    sextile = 6
)

# the complete config object
config = Config(
    theme_type = "light", # or "dark", "mono"
    display = display,
    orb = orb
)

# create data object with the config
data = Data(
    name = "MiMi",
    utc_dt = "1980-04-20 06:30",
    lat = 25.0531,
    lon = 121.526,
    config = config,
)
```

## Tech Stack

- [tagit]: SVG / HTML generation and manipulation
- [pyswisseph]: astrological data - Swiss Ephemeris

[demo.ipynb]: https://github.com/hoishing/natal/blob/main/demo.ipynb
[pyswisseph]: https://github.com/astrorigin/pyswisseph
[Swiss Ephemeris]: https://www.astro.com/swisseph/swephinfo_e.htm
[tagit]: https://github.com/hoishing/tagit

"""
Plotting Data
=============

In this example, we plot some data obtained from a Tradesman model.
"""

# %%

# Imports
from os.path import join
from uuid import uuid4
from tempfile import gettempdir

import geopandas as gpd
import folium
import branca

from aequilibrae.utils.db_utils import commit_and_close
from tradesman.utils import create_example

# %%
# Let's import our example

folder_path = join(gettempdir(), uuid4().hex)

project = create_example(folder_path)

# %%
# Let's create a path to the project database. It will help us get the geometry data we need.
db_path = project.project_base_path / "project_database.sqlite"

# %%
# Let's import some information about our model's TAZs.
with commit_and_close(db_path, spatial=True) as conn:
    zones = gpd.read_postgis("SELECT *, ST_AsBinary(geometry) geom FROM zones;", con=conn, geom_col="geom", crs=4326)
    zones.drop(columns=["geometry"], inplace=True)

# %%
# From AequilibraE version 1.5.0, the context manager can be replaced with:

# with proj.db_connection_spatial as conn:

# %%
# Create a population density field
zones["pop_density"] = zones["population"] / (zones["geom"].to_crs(3857).area * 10e-6)

# %%
# Let's plot our data!
zones.explore(
    "pop_density",
    tiles="CartoDB positron",
    cmap="Greens",
    tooltip=False,
    style_kwds={"fillOpacity": 1.0},
    zoom_start=11,
    location=[-29.935717, -71.260520],
    popup=True,
)
# %%
# Total female population per zone
zones["female_pop"] = zones[[f"f_pop_{i}" for i in range(1, 19)]].sum(axis=1)
# Total male population per zone
zones["male_pop"] = zones[[f"m_pop_{i}" for i in range(1, 19)]].sum(axis=1)
# Ratio of the male population with respect to the female population
zones["pop_ratio"] = zones.male_pop / zones.female_pop

# %%
zones.explore(
    "pop_ratio",
    tiles="CartoDB positron",
    cmap="RdPu",
    tooltip=False,
    style_kwds={"fillOpacity": 1.0},
    zoom_start=11,
    location=[-29.935717, -71.260520],
    popup=True,
)

# %%
# In an ideal scenario, the ratio of the male population with respect to the female population would be close to 1.06. In countries such as India or China, this ratio is a bit larger, 1.12 and 1.15, respectively. This difference is responsible for creating abnormal sex ratios at birth.

# %%
# Now, let's analyze the median age of male and female inhabitants per zone.
# To plot this data, we shall do a little bit of math first, as our data is represented in intervals.

interval_min = [0, 1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80]
interval_mean = [0.5, 3, 7.5, 12.5, 17.5, 22.5, 27.5, 32.5, 37.5, 42.5, 47.5, 52.5, 57.5, 62.5, 67.5, 72.5, 77.5, 82.5]
interval_range = [1, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]

for sex in ["f", "m"]:
    columns = [col for col in zones.columns if f"pop_{sex}_" in col]
    list_values = zones[columns].to_numpy()

    median_values = []

    for idx, lst in enumerate(list_values):
        median = lst.sum() / 2
        counter = 0
        for pos, element in enumerate(lst):
            counter += element
            if counter > median:
                counter -= element
                break

        median_values.append(interval_min[pos - 1] + ((median - counter) * (interval_range[pos - 1] / lst[pos - 1])))

    zones[f"median_age_{sex}"] = median_values

# %%
# Let's take a look at our data!
fig = branca.element.Figure()

subplot1 = fig.add_subplot(1, 2, 1)
subplot2 = fig.add_subplot(1, 2, 2)

map1 = folium.Map(location=[-29.935717, -71.260520], zoom_start=12)
map1 = zones.explore(
    m=map1,
    column="median_age_f",
    linewidth=0.1,
    cmap="Oranges",
    scheme="equal_interval",
    k=5,
    legend=False,
    legend_kwds={"loc": "upper left", "fmt": "{:.2f}"},
    tiles="CartoDB positron",
)
folium.LayerControl().add_to(map1)

map2 = folium.Map(location=[-29.935717, -71.260520], zoom_start=12)
map2 = zones.explore(
    m=map2,
    column="median_age_m",
    linewidth=0.1,
    cmap="Blues",
    legend=False,
    scheme="equal_interval",
    k=5,
    legend_kwds={"loc": "upper left", "fmt": "{:.2f}"},
    tiles="CartoDB positron",
)
folium.LayerControl().add_to(map2)

subplot1.add_child(map1)
subplot2.add_child(map2)

fig

# %%
# Finally, let's check out our model's network.
# As we imported data from OpenStreetMaps, it is possible that we have several _link_type_ categories. We'll plot only five of them.
with commit_and_close(db_path, spatial=True) as conn:
    qry = "SELECT link_type, distance, modes, ST_AsBinary(geometry) geom FROM links;"
    links = gpd.read_postgis(qry, con=conn, geom_col="geom", crs=4326)
    links = links[links.link_type.isin(["motorway", "trunk", "primary", "secondary", "tertiary"])]

# %%
colors = ["#219EBC", "#ffb703", "#8ECAE6", "#023047", "#fb8500"]
m = None

for idx, tp in enumerate(links.link_type.unique()):
    gdf = links[links.link_type == tp]
    if m:
        gdf.explore(
            m=m,
            name=tp,
            tiles="CartoDB positron",
            tooltip=False,
            popup=True,
            zoom_start=11,
            location=[-29.935717, -71.260520],
            legend=False,
            color=colors[idx],
        )
    else:
        m = gdf.explore(
            name=tp,
            tiles="CartoDB positron",
            tooltip=False,
            popup=True,
            zoom_start=11,
            location=[-29.935717, -71.260520],
            legend=False,
            color=colors[idx],
        )

folium.LayerControl().add_to(m)

m

# %%
project.close()

"""
Plotting Data
=============

In this example, we plot some data from a Tradesman model.
If you're familiar with AequilibraE, this is similar to the Coquimbo example with
randomly generated population data.
"""

# %%

# Imports
from os.path import join
from uuid import uuid4
from tempfile import gettempdir

import geopandas as gpd
import folium
import branca
import numpy as np

from aequilibrae.utils.db_utils import commit_and_close
from tradesman.utils import create_model_example

# %%

# Let's import our example
folder_path = join(gettempdir(), uuid4().hex)

model = create_model_example(folder_path)

# %%

# Let's create a path to the project database. It will help us get the geometry data we need.
db_path = model.project.project_base_path / "project_database.sqlite"

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
age = [0, 1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80]
# Total female population per zone
zones["female_pop"] = zones[[f"f_pop_{i}" for i in age]].sum(axis=1)
# Total male population per zone
zones["male_pop"] = zones[[f"m_pop_{i}" for i in age]].sum(axis=1)
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
def grouped_data_median(data, class_limits):
    midpoints = np.array([(lim[0] + lim[1]) / 2 for lim in class_limits])

    medians = np.zeros(data.shape[0])

    for i, row in enumerate(data):
        n = np.sum(row)
        median_pos = n / 2
        cum_freq = np.cumsum(row)
        median_class = np.argmax(cum_freq >= median_pos)
        prev_cum_freq = cum_freq[median_class - 1] if median_class > 0 else 0
        class_freq = row[median_class]
        lower_limit = class_limits[median_class][0]
        upper_limit = class_limits[median_class][1]
        class_width = upper_limit - lower_limit
        if class_freq > 0:
            median = lower_limit + ((median_pos - prev_cum_freq) / class_freq) * class_width
        else:
            median = midpoints[median_class]
        medians[i] = median

    return medians


# %%
# Now, let's analyze the median age of male and female inhabitants per zone.
# To plot this data, we shall do a little bit of math first, as our data is represented in intervals.
class_limit = list(zip(age[:-1], age[1:]))

for sex in ["f", "m"]:
    columns = [col for col in zones.columns if f"{sex}_pop_" in col]
    list_values = zones[columns].to_numpy()

    median_values = grouped_data_median(list_values, class_limit)

    zones[f"{sex}_median_age"] = median_values

# %%
# Let's take a look at our data!
fig = branca.element.Figure()

subplot1 = fig.add_subplot(1, 2, 1)
subplot2 = fig.add_subplot(1, 2, 2)

map1 = folium.Map(location=[-29.935717, -71.260520], zoom_start=12)
map1 = zones.explore(
    m=map1,
    column="f_median_age",
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
    column="m_median_age",
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
links = model.project.network.links.data
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
# Finally, we close the model.
model.close()

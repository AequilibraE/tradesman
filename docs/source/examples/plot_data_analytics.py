"""
Plotting Data
=============

In this example, we plot some data from a Tradesman model. If you're familiar with AequilibraE,
it corresponds to the Coquimbo example with randomly generated population data.
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

from tradesman.utils import create_model_example
# sphinx_gallery_thumbnail_path = '../images/model.png'

# %%

# Let's create our example
folder_path = join(gettempdir(), uuid4().hex)

model = create_model_example(folder_path)

# %%
# Let's import some information about our model's TAZs.

with model.project.db_connection_spatial as conn:
    qry = "SELECT *, ST_AsBinary(geometry) geom FROM zones;"
    zones = gpd.read_postgis(qry, con=conn, geom_col="geom", crs=4326)
    zones.drop(columns=["geometry"], inplace=True)

# %%
# The import method above is verbose but corresponds to the one used for importing political
# subdivisions or other spatial data that do not belong to the default AequilibraE project.
#
# To import zoning data directly from the project, you can use:
# zones = model.project.zoning.data

# %%
# Create a population density field
zones["pop_density"] = zones["population"] / (zones["geom"].to_crs(3857).area * 10e-6)

# %%
map_location = [-29.935717, -71.260520]
# %%
# Let's plot our data!
zones.explore(
    "pop_density",
    tiles="CartoDB positron",
    cmap="Greens",
    tooltip=False,
    style_kwds={"fillOpacity": 1.0},
    zoom_start=11,
    location=map_location,
)

# %%
# In an ideal scenario, the ratio of the male population with respect to the female population
# would be close to 1.06. In countries such as India or China, this ratio is a bit larger, 1.12
# and 1.15, respectively. This difference is responsible for creating abnormal sex ratios at birth.

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
    location=map_location
)

# %%
# Now, let's analyze the median age of male and female inhabitants per zone.
# To plot this data, we shall do a little bit of math first, as our data is represented in intervals.

from math import ceil

# %% 
def grouped_data_median(data):
    cvalues = np.cumsum(data, axis=1)
    median_values = []
    for _, val in enumerate(cvalues):
        if val[-1] % 2 == 0:
            median = val[-1] / 2
            next_element = median + 1
            for idx, element in enumerate(val):
                if median <= element:
                    a = age[idx]
                if next_element <= element:
                    b = age[idx]
                    break
            median_values.append(int((a + b) / 2))
        else:
            median = ceil(val[-1] / 2)
            for idx, element in enumerate(val):
                if median <= element:
                    median_values.append(age[idx])
                    break
    
    return median_values

# %%
for sex in ["f", "m"]:
    columns = [col for col in zones.columns if f"{sex}_pop_" in col]
    list_values = zones[columns].to_numpy()

    median_values = grouped_data_median(list_values)

    zones[f"{sex}_median_age"] = median_values

# %%
# Let's take a look at our data!
fig = branca.element.Figure()

subplot1 = fig.add_subplot(1, 2, 1)
subplot2 = fig.add_subplot(1, 2, 2)

map1 = zones.explore(
    "f_median_age",
    tiles="CartoDB positron",
    cmap="Oranges",
    tooltip=False,
    legend=False,
    style_kwds={"fillOpacity": 1.0},
    zoom_start=11,
    location=map_location
)

map2 = zones.explore(
    "m_median_age",
    tiles="CartoDB positron",
    cmap="Blues",
    tooltip=False,
    legend=False,
    style_kwds={"fillOpacity": 1.0},
    zoom_start=11,
    location=map_location
)

subplot1.add_child(map1)
subplot2.add_child(map2)

fig

# %%
# Finally, let's check out our model's network.
# As we imported data from OpenStreetMaps, it is possible that we have several 'link_type' categories.
# We'll plot only five of them.
ltypes = ["motorway", "trunk", "primary", "secondary", "tertiary"]
links = model.project.network.links.data
links = links[links.link_type.isin(ltypes)]

# %%
colors = ["#219EBC", "#ffb703", "#8ECAE6", "#023047", "#fb8500"]
m = None

for idx, tp in enumerate(ltypes):
    gdf = links[links.link_type == tp]
    if m:
        gdf.explore(
            m=m,
            name=tp,
            tiles="CartoDB positron",
            tooltip=False,
            zoom_start=11,
            location=map_location,
            legend=False,
            color=colors[idx],
        )
    else:
        m = gdf.explore(
            name=tp,
            tiles="CartoDB positron",
            tooltip=False,
            zoom_start=11,
            location=map_location,
            legend=False,
            color=colors[idx],
        )

folium.LayerControl().add_to(m)

m

# %%
# Finally, we close the model.
model.close()

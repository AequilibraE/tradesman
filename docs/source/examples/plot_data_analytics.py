"""
Plotting Data
=============

On this example, we plot some data obtained from a Tradesman model.
"""

# %%
# Imports
import os

os.environ["USE_PYGEOS"] = "0"

import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as cx
import folium

from tradesman.utils.create_tradesman_example import create_tradesman_example
from tempfile import gettempdir
from uuid import uuid4
from os.path import join

# %%
# Let's create our project and establish a connection
prj = create_tradesman_example(join(gettempdir(), uuid4().hex))

cnx = prj.conn

# %%
# Let's identify the region we are plotting our data.
# First we import our subdivisions

subdivisions = gpd.read_postgis(
    "SELECT division_name, level, ST_AsBinary(geometry)geom FROM political_subdivisions;",
    con=cnx,
    geom_col="geom",
    crs=4326,
)

# %%
# Now we can plot our map!
# Go ahead and check it out
colors = ["#01BEFE", "#FFDD00", "#FF7D00", "#FF006D", "#ADFF02", "#8F00FF"]
m = None

for lvl in range(-1, subdivisions.level.max() + 1):
    gdf = subdivisions[subdivisions.level == lvl]

    if m:
        gdf.explore(
            m=m,
            name=f"level {lvl}",
            tiles="CartoDB positron",
            tooltip=False,
            popup=True,
            location=[-0.52943, 166.9346],
            zoom_start=13,
            legend=False,
            color=colors[lvl + 1],
        )
    else:
        m = gdf.explore(
            name=f"model_area",
            tiles="CartoDB positron",
            tooltip=False,
            popup=True,
            location=[-0.52943, 166.9346],
            zoom_start=13,
            legend=False,
            color=colors[lvl + 1],
        )

folium.LayerControl().add_to(m)

m
# %%
# Feel free to turn on/off all the layers. If you click in the subdivisions, you can also check its name and level.

# %%
# Now let's move on and import some information about our model's TAZs.
zones = gpd.read_postgis("SELECT *, ST_AsBinary(geometry) geom FROM zones;", con=cnx, geom_col="geom", crs=4326)
zones.drop(columns=["geometry"], inplace=True)

# %%
# And create new columns
# Population per square kilometer
zones["POP_DENSITY"] = zones["population"] / (zones["geom"].to_crs(3857).area * 10e-6)

# %%
# Let's plot our data!
zones.explore(
    "POP_DENSITY",
    tiles="CartoDB positron",
    cmap="Greens",
    tooltip=False,
    style_kwds={"fillOpacity": 1.0},
    zoom_start=13,
    location=[-0.52943, 166.9346],
    popup=True,
)
# %%
# Total female population per zone
zones["TOTALF_POP"] = zones[[f"POPF{i}" for i in range(1, 19)]].sum(axis=1)
# Total male population per zone
zones["TOTALM_POP"] = zones[[f"POPM{i}" for i in range(1, 19)]].sum(axis=1)
# Ratio of male population with respect to female population
zones["PP_FM"] = zones.TOTALM_POP / zones.TOTALF_POP

# %%
zones.explore(
    "PP_FM",
    tiles="CartoDB positron",
    cmap="RdPu",
    tooltip=False,
    style_kwds={"fillOpacity": 1.0},
    zoom_start=13,
    location=[-0.52943, 166.9346],
    popup=True,
)

# %%
# In an ideal scenario, the ratio of male population with respect to female population would be close to 1.06. In countries such as India or China, this ratio is a bit larger, 1.12 and 1.15, respectively. This difference is responsible for creating an abnormal sex ratios at birth.

# %%
# Now, let's analyze the median age of male and female inhabitants per zone.
# To plot this data, we shall do a little bit of math first, as our data is represented in intervals.

interval_min = [0, 1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80]
interval_mean = [0.5, 3, 7.5, 12.5, 17.5, 22.5, 27.5, 32.5, 37.5, 42.5, 47.5, 52.5, 57.5, 62.5, 67.5, 72.5, 77.5, 82.5]
interval_range = [1, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]

for sex in ["F", "M"]:
    list_values = zones[[f"POP{sex}{i}" for i in range(1, 19)]].to_numpy()

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

    zones[f"MEDIAN_AGE_{sex}"] = median_values

# %%
# Let's take a look in our data!
fig, ax = plt.subplots(1, 2, constrained_layout=True, frameon=False, figsize=(12, 8))

zones.plot(
    ax=ax[0],
    column="MEDIAN_AGE_F",
    linewidth=0.1,
    edgecolor="black",
    facecolor="whitesmoke",
    cmap="Oranges",
    scheme="equal_interval",
    k=5,
    legend=True,
    legend_kwds={"loc": "upper left", "fmt": "{:.2f}"},
)
cx.add_basemap(ax[0], crs=4326, source=cx.providers.Stamen.TonerLite)

zones.plot(
    ax=ax[1],
    column="MEDIAN_AGE_M",
    linewidth=0.1,
    edgecolor="black",
    facecolor="whitesmoke",
    cmap="Blues",
    legend=True,
    scheme="equal_interval",
    k=5,
    legend_kwds={"loc": "upper left", "fmt": "{:.2f}"},
)
cx.add_basemap(ax[1], crs=4326, source=cx.providers.Stamen.TonerLite)

fig.show()

# %%
# Our model also has OpenStreetMaps Building information. Let's take a look at the location of some building types.

# %%
# Import the data
qry = "SELECT building, zone_id, ST_AsBinary(geometry)geom FROM osm_building WHERE geometry IS NOT NULL;"
buildings = gpd.read_postgis(qry, con=cnx, geom_col="geom", crs=4326)
buildings = buildings[buildings.building.isin(["undetermined", "Religious", "residential", "commercial"])]

# %%
# And plot it
colors = ["#73b7b8", "#0077b6", "#f05a29", "#f05a29"]

m = None

for idx, bld in enumerate(buildings.building.unique()):
    gdf = buildings[buildings.building == bld]

    if m:
        gdf.explore(
            m=m,
            name=bld,
            tiles="CartoDB positron",
            tooltip=False,
            popup=True,
            zoom_start=13,
            location=[-0.52943, 166.9346],
            legend=False,
            color=colors[idx],
        )
    else:
        m = gdf.explore(
            name=bld,
            tiles="CartoDB positron",
            tooltip=False,
            popup=True,
            zoom_start=13,
            location=[-0.52943, 166.9346],
            legend=False,
            color=colors[idx],
        )

folium.LayerControl().add_to(m)

m

# %%
# Finally, let's check out our model's network.
# As we imported data from OpenStreetMaps, it is possible that we have several _link_type_ categories. We'll plot only five of them.
links = gpd.read_postgis(
    "SELECT link_type, distance, modes, ST_AsBinary(geometry) geom FROM links;", con=cnx, geom_col="geom", crs=4326
)
links = links[links.link_type.isin(["unclassified", "residential", "primary", "track", "tertiary"])]

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
            zoom_start=13,
            location=[-0.52943, 166.9346],
            legend=False,
            color=colors[idx],
        )
    else:
        m = gdf.explore(
            name=tp,
            tiles="CartoDB positron",
            tooltip=False,
            popup=True,
            zoom_start=13,
            location=[-0.52943, 166.9346],
            legend=False,
            color=colors[idx],
        )

folium.LayerControl().add_to(m)

m

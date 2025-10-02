"""
Create model
============

In this example, we show how to run a complete Tradesman model for Nauru, an insular country in
Oceania.
"""

# %%
# Imports
from tradesman.model import Tradesman
from tempfile import gettempdir
from uuid import uuid4
from os.path import join

# sphinx_gallery_thumbnail_path = '../images/model.png'

# %%
# We create a temporary folder to store our data
folder = join(gettempdir(), uuid4().hex)

# %%
# Let's initialize our model
model = Tradesman(network_path=folder, model_place="Nauru")

# %%
# If we want to run a complete Tradesman model using its default configurations, we can use

# model.create()

# %%
# The command above comprises all the steps below to create a complete model from scratch.
#
# However, we can also customize the model we want to create, set up the size of the zones,
# decide whether to import the network, gender population data, and so on. So let's check out
# how to change some configurations.

# %%
# First step is to add the model area and other political subdivisions to our model
model.import_model_area()
model.add_country_borders()
model.import_subdivisions()

# %%
# We won't download the network from OpenStreetMap for now, but you can try it out by
# uncommenting the line below.

# model.import_network()

# %%
# Later we import population data into our model. We use WorldPop as our source, but you can also
# try Meta.
model.import_population()

# %%
# Now that we have network and population information, we can build our Traffic Analysis Zones
# (TAZs). Nauru has a small population, so we will set our zones to range between 100 and 500
# inhabitants.
model.build_zoning(min_zone_pop=100, max_zone_pop=500)

# %%
# We can gather information about total inhabitants by sex and age. Again, we won't do it now, but
# you can uncomment the code block below to try it out.

# model.import_pop_by_sex_and_age()

# %%
# We can also import amenity (points of interest) and building information from Overture Maps.
# Let's try importing amenities.

model.import_amenities()

# %%
# We won't import buildings now, but you can try it out by uncommenting the code block below.

# model.import_buildings()

# %%
# Finally, let's close the model.
model.close()

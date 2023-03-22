"""
Create model
============

In this example, we show how to run a complete Tradesman model for Nauru, an insular country in Oceania.
"""

# %%
# Imports
from tradesman.model import Tradesman
from tempfile import gettempdir
from uuid import uuid4
from os.path import join

# %%
# We create a temporary folder to store our data
folder = join(gettempdir(), uuid4().hex)

# %%
# Let's initialize our model
model = Tradesman(network_path=folder, model_place="Nauru")

# %%
# If we want to run a model with Tradesman default configurations, we can go for `model.create()` and wait for it.
# But we can customize the model we want to create. So let's check out how to change some of the configurations.

# %%
# First step is to add the model area and other geographical subdivisions to our model
model.import_model_area()
model.add_country_borders()
model.import_subdivisions()

# %%
# We can now import the network to our model. We'll download our network from OpenStreetMaps (OSM).
model.import_network()

# %%
# Later we import population data into our model. We use WorldPop as our source, but you can also try Meta.
model.import_population()

# %%
# Now that we have network and population information, we can build our Traffic Analysis Zones (TAZs).
# Nauru has a small population, so we will set our zones to range between 100 and 500 inhabitants.
model.build_zoning(min_zone_pop=100, max_zone_pop=500)

# %%
# Let's import more population data to our model!
# Now we'll gather information about total inhabitants by sex and age.
model.import_pop_by_sex_and_age()

# %%
# We can also import amenity and building information from OSM.
model.import_amenities()
model.import_buildings(False)

# %%
# With Tradesman, we can also create a synthetic population for our model.
# First, we build our seed sample. At the end of this step, it is possible to see the overall characteristics of
# our population sample.

# %%
model.build_population_synthesizer_data(sample_size=0.02)

# %%
# Than we synthesize our data.
# As our population is not that large, we don't need to set multiple threads to run the synthesizer.
# But as the size of the population increases, it is worth using multiple threads to reduce the processing time.
# At the end of the process, we will receive two outputs related to the validation of our synthetic population.

# %%
model.synthesize_population(thread_number=1)

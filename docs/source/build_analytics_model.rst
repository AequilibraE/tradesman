.. _build_analytics_model:

Analytics models
================

The backbone of the analytics pipeline consists in building road network models 
from `Open-Street Maps (OSM)<https://www.openstreetmap.org/>`_ data and incorporates population information
from the raster layers available at the  `Humanitarian Data Exchange
<https://data.humdata.org/>`_.

1. Building Road network model
2. Incorporating population data

   * Importing raw population data
   * Aggregating population into analysis zones
   * Importing population pyramid data

3. Incorporating amenity and building data
4. Calculate Rural Access Index

At the end of the creation of the analytics models, the user will have a
all their data inside and :ref:`aequilibrae` model, which is a Python-native
transport modelling software. In turn, all files used in AequilibraE are
open-format (SQLite, Spatialite) and can be used by virtually any current data
and GIS software/platform available.

Building the road network model
_______________________________

The first step in the analytics setup process is the development of the Road
Network model from OSM data.

This step includes the following sub-steps:

* Downloading and interpreting (parsing) the OSM network
* Downloading the country borders from Open-Street Maps
* Making sure that only links from within the country borders are kept in the
  model
* Veryfing if the network can be used for computing routes from two arbitrary
  points

Use Cases enabled:
~~~~~~~~~~~~~~~~~~

* Displaying general stats regarding link types and pavement surfaces

* Displaying specific stats for bridges, tolls, and tunnels and their link types
  and pavement surfaces

Incorporating population data
_____________________________

As mentioned above, the population information we use in this analytics pipeline
are obtained directly from the `Humanitarian Data Exchange
<https://data.humdata.org/>`_ and come on a raster (i.e. image) format, and it
is therefore inadequate for performing the type of analytics we are interested
in.

This results on a process that has is significantly more complex when compared
to the creation of the Road network model, so it is comprised of 3 different
Jupyter Notebooks that allow the user to import the raw population data and to
aggregate it into a level of geographic detail that is compatible with the
specific needs.

The importing of raw population data consists in getting the country population 
information from a raster image or file and importing them to the analitics data
model as a geographic layer of points, each one of which representing a pixel of the
original image and carrying the population attributed to that pixel.

This process includes the following steps:

* Converting the population layer image to points that are contained within
  the country borders for our model
* Importing this point layer into a *raw_population* layer inside our model
  database
* Comparing the total vectorized population to a (`World Bank source
  <https://data.worldbank.org/indicator/SP.POP.TOTL>`_)

Importing amenity and buildings
_______________________________

The amenity and building information we use is obtained directly from the
OSM. Both amenity and building information provides us useful information regarding
land-use. Later, we can use this information as an input for the trip
generation model.

Calculate Rural Access Index
_____________________________

:ref:`RAI <rural_access_index>` is an useful index, and represents the percentage of 
rural people who live within a two-kilometer radius from an all-seasoned road.

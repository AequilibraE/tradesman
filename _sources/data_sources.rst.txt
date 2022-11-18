.. _data_sources:

Data sources
============

To be part of the backbone of a model build, all data sources
have to fulfill the following requirements:

- Coverage: Must be available for most if not all countries in the world.

- Openness: The data must be free, open and cannot impose excessive red-tape for
  its use.

- Trustworthiness: The science and/or practices behind the development of
  data source must be technically transparent and robust, and have documented
  use in research and/or practice.

Road network
------------

All the road network data is obtained directly from `Open-Street Maps (OSM)
<https://www.openstreetmap.org/>`_, which is the de-facto standard for
open transportation network data. More information about it can be found on
its `website <https://www.openstreetmap.org/about>`_.

Political Subdivisions
----------------------

Political Subdivisions can be downloaded from either `GADM <https://gadm.org/data.html>`_
or `geoBoundaries <https://www.geoboundaries.org/>`_. Both databases are open, and
provide information with respect to countries and territories, and the existing political
subdivisions that might exists.

Point-of-Interest
-----------------

A Point-of-Interest (POI) represents a particular feature in the space, like  
churches, schools, pubs, or tourist attractions. It does not necessarily have to 
be a point, but can also be other OSM elements, such as nodes or ways. 

It is worth reminding that the "interest" part should not be considered too 
literally, once a feature can be quite ordinary, such as a postbox. In this case,
these features are usually considered ``amenity``.

Amenities are useful and import facilities for visitors and residents. More
information on amenity values in OSM, is available `in this page <https://wiki.openstreetmap.org/wiki/Key:amenity>`_.

A building can also be a POI. The OSM building tag is used to identify individual
buildings or groups of connected buildings, and can assume several values.
More information on building values can be found in `this page <https://wiki.openstreetmap.org/wiki/Buildings>`_.

Building footprints
-------------------
Building footprints can also be downloaded from OSM or from data generated through
image recognition by `Microsoft <https://github.com/microsoft/GlobalMLBuildingFootprints>`_.

Population
----------

There are currently two data sources of spatialized population that are suitable
for use in this project.

1. `Meta High Resolution Population density Maps
   <https://dataforgood.facebook.com/dfg/tools/high-resolution-population-density-maps>`_

2. `World Pop <https://www.worldpop.org/about>`_

Both data sources provide population estimates at a very high resolution (down
to a grid of 100x100m) and are based on extensive research and offer similar
results at more aggregate levels (small cities or neighborhoods within a large
city), so they are equivalent for the purposes of building models for large areas.

However, the World Pop data includes estimates with finer detail with respect
to population per age bracket, which can be crucial when analyzing access to
hospital infrastructure, schools and the labor market, so we have decided
to use that data source.

The `list of links for download
<https://www.github/pedrocamargo/road_analytics/blob/main/model/population/all_raster_pop_age_and_sex_source.csv>`_
while the data for the total population is listed on a
`separate file
<https://www.github/pedrocamargo/road_analytics/blob/main/model/population/all_raster_pop_source.csv>`_.

All the data is downloaded from the `Humanitarian Data Exchange
<https://data.humdata.org/>`_, which provides a convenient interface for data
download.

.. _data_sources:

Data sources
============

To be included in the main portions of thisanalytics pipeline, all data sources
have to fulfill the following requirements:

- Coverage: Since this pipeline is designed to be deployable for any country in
  the world, the data source must be available for the vast majority of
  countries on Earth.

- Openess: The data must be free, open and cannot impose excessive red-tape for
  its use

- Trustworthiness: The science and/or practices behind the development of
  data source must be technically transparent and robust, and have documented
  use in research and/or practice.

Road network
------------

All the road network data is obtained directly from `Open-Street Maps (OSM)
<https://www.openstreetmap.org/>`_, which is the de-facto standard for
open transportation network data. More information about it can be found on
its `website <https://www.openstreetmap.org/about>`_.


Point-of-Interest
-----------------
XXXXXXXXX INCLUDE DISCUSSION ON OSM DATA    XXXXXXXXXXXXXXXXXXXXXXXX

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
city), so they are equivalent for the purposes of this analytics pipeline.

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

Commuting Zones
---------------

The Commuting zones dataset provided by Meta consists of identifying areas
within which people live and work, which is extremely relevant for providing
reference values for our transportation demand model, as discussed in the
corresponding section.

Data documentation can be found on its `website
<https://dataforgood.facebook.com/dfg/tools/commuting-zones>`_.

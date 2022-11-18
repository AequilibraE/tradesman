.. _zoning_system:

Building Zones
==============

*The definition of a zone system is, traditionally, a somewhat manual exercise of*
*aggregating adjacent geographical subdivisions such as census tracts into zones*
*such that the level of detail is compatible with the network density and desired*
*precision.* [PVC2022]_
Very small land subdivisions cannot be expected to be available, or even exist,
for the vast majority of the countries on Earth, and since a laborious manual
exercise is exactly one of the activities that this package aims to eliminate,
the traditional process was not considered as an alternative, but rather
Tradesman adopts the methodology developed in [PVC2021]_ and further developed in
[PVC2022]_ to design zoning systems.

As described in [PVC2022]_ (with some modifications to suit this documentation):

*In a nutshell, this methodology consists in building a mesh of small hexagonal*
*polygons covering the area of interest and computing the estimated population*
*of each polygon from raster data (Open Spatial Demographic Data and Research -*
*WorldPop n.d.). With these “micro-zones” in hand, we can recursively apply*
*spatial clustering algorithms to create bigger zones with a maximum population*
*per zone.*

*When applying the spatial clustering procedures, we limited the clustering to*
*base hexagons that were (mostly) in the same district/county (or equivalent political*
*subdivision) and prevent disconnect zones from existing. As a result, many zones*
*with much smaller populations than the original target, can also created, but zone *
*aggregations do a remarkable job in matching the political subdivisions.*

*This population-based criteria, we obtain a zoning system that is more*
*detailed in heavily populated areas and much coarser in unpopulated regions of*
*the country.*

Tradesman utilizes as default a hexbin mesh with 200m of sides and zone size targets
of a minimum of 500 people and a maximum of 10,000.

References
----------

.. [PVC2021] https://trb-planningapp.secure-platform.com/a/solicitations/53/sessiongallery/726/
.. [PVC2022] https://australasiantransportresearchforum.org.au/network-resilience-analysis-with-large-streams-of-mobility-data-and-open-source-software/

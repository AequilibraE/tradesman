.. _concepts:

General concepts
================



4-step models
-------------

The 4-step model is a classical transportation model. In a very simplistic way,
it consists in input populational, economical, and network data into a model,
that can generate, estimate, split, and allocate the existing demand.

Trip generation is the first step. It consists in predicting the number of trips
generated and attracted to each zone in the analysis. Despite our intuition, for
transportation matters, a trip is associated with a one-way movement. As an example,
if we leave our home, go to the city hall, and then return home, it means that we
just made two trips, and not only one. Trip generation step studies the
relationships between the trips undertook and socio-economical characteristics
from users and zones.

Later, comes the distribution of these trips. In a simplistic way, in this step all
trips generated are going to be distributed across the study zones. The aim of trip
distribution is to investigate the mutual attraction between zones. The result of
this step is a matrix, a table that associates the number of trips that have origin
and destination to each one of the study zones. This matrix is used as input in the
following step.

Modal split is the following step. In this step, the data from the origin/destination
matrix is going to be split into different transportation modes. The goal of modal
split is answering which mode of transportation will affect people’s choice. It is
important to keep in mind that there are internal and external factors that influence
the choice of transportation mode, such as income, household structure and location,
trip purposes, travel time, safety, and convenience.

The final step consists in assigning the existing demand to the existing transportation
network. In the demand assignment, an interaction between demand for transportation
(with the data generated in the past steps) and the available transportation offer
happens. It aims to assign people and vehicles to road and public transport networks,
so it turns out to be both a route choice and a demand distribution problem.

.. _aequilibrae:

AequilibraE
~~~~~~~~~~~

AequilibraE is the first comprehensive Python package for transportation
modeling, and it aims to provide all the resources not easily available from
other open-source packages in the Python (NumPy, really) ecosystem.

Comprehensive documentation is available in its `website
<http://aequilibrae.com/python/latest/>`_.


Road Networks model
-------------------

Road network model is based on data imported directly from OSM. The road network
information provides information on the kind of road, and its surface, whenever
available.

With respect to the kind of road, OSM classification distinguish them by function
and importance rather by their physical characteristics or legal classification. More
information on the `kind of road webpage <https://wiki.openstreetmap.org/wiki/Key:highway>`.

Regarding surface, OSM values provide additional information about the physical surface of
roads, and some other features, such as material composition and/or structure. All data
values for road surface can be found in `their OSM webpage <https://wiki.openstreetmap.org/wiki/Key:surface>`.


Rural Access Index
------------------

The Rural Access Index (RAI) is a transportation indicator endorsed by the World
Bank, and it measures the number of rural people who live within two kilometers
of an "all-seasoned road" as a porpotion of the total rural population. The two
kilometers distance is equivalent to a 20-25 minute walk, and an "all-seasoned road"
is a road that is motobrable all year round by vehicles that are not
four-wheel-drive, which can accept occasional interruptions of short duration
during inclement weather (e.g. heavy rainfall), especially in lightly trafficked
roads. For more informations with respect to RAI, we suggest the `World Bank webpage
<https://openknowledge.worldbank.org/handle/10986/17414>`.


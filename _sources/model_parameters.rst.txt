.. _model_parameters:

Model Parameters
================

.. _road_capacities:

Road capacities
_______________

+--------------------------+-----------+--------------+-----------+
| link types               | lanes per | capacity per | speed     |
| from OSM                 | direction | lane (veh/h) | (km/h)    |
+--------------------------+-----------+--------------+-----------+
| roundabout               |     1     |     250      |    40     |
+--------------------------+-----------+--------------+-----------+
| residential              |           |              |           |
| service, living_street   |           |              |           |
| road, rest_area, escape, |     1     |    400       |    40     |
| bus, services, corridor  |           |              |           |
| passing_place &          |           |              |           |
| emergency_access_point   |           |              |           |
+--------------------------+-----------+--------------+-----------+
|  tertiary                |     1     |     500      |    50     |
+--------------------------+-----------+--------------+-----------+
|  unclassified            |     1     |     600      |    40     |
+--------------------------+-----------+--------------+-----------+
| secondary                |     1     |     400      |    60     |
+--------------------------+-----------+--------------+-----------+
| primary                  |     1     |     700      |    60     |
+--------------------------+-----------+--------------+-----------+
|     trunk                |     1     |     900      |    60     |
+--------------------------+-----------+--------------+-----------+
|   motorway & freeway     |     2     |    1400      |   100     |
+--------------------------+-----------+--------------+-----------+
| cycleway, track, footway,|           |              |           |
| path, steps, pedestrian, |    0      |      0       |    5      |
| closed & disused         |           |              |           |
+--------------------------+-----------+--------------+-----------+
| OTHER (NON LISTED)       |     1     |     400      |    40     |
+--------------------------+-----------+--------------+-----------+

.. _pavement_constraints:

Pavement Limitations
____________________

+--------------------------+-----------+--------------+
| link types               | speed     | capacity     |
| from OSM                 | multiplier| multiplier   |
+--------------------------+-----------+--------------+
| asphalt, paved, concrete |     1     |      1       |
+--------------------------+-----------+--------------+
| pebblestone, cobblestone |   0.7     |     0.7      |
| paving_stones & gravel   |           |              |
+--------------------------+-----------+--------------+
| rock & fine_gravel       |    0.6    |    0.6       |
+--------------------------+-----------+--------------+
| ground, grass, dirt &    |    0.5    |    0.5       |
| compacted                |           |              |
+--------------------------+-----------+--------------+
| OTHER (NON LISTED)       |     1     |      1       |
+--------------------------+-----------+--------------+


.. _trip_generation_parameters:

Trip Generation Parameters
--------------------------
XXXXXXXXXXXXXXXXXX


.. _trip_distribution_parameters:

Trip Distribution Parameters
--------------------------
XXXXXXXXXXXXXXXXXX

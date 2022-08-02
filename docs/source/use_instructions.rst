.. _use_instructions:

Using this software
===================

Tradesman is a Python package that lets you build transportation models. You can
build transportation networks importing data from OSM, import political sub-divisions,
population information, amenities, and building information, as well as create zones.
At the end, the user will have all their data inside and :ref:`aequilibrae` model, 
which is a Python-native transport modelling software. In turn, all files used in 
AequilibraE are open-format (SQLite, Spatialite) and can be used by virtually any 
current data and GIS software/platform available.

Usage
~~~~~

To get started with Tradesman, read its user reference and work through its examples
repo for introductory usage demonstrations and sample code.

Tradesman is built on top of AequilibraE and interacts with OpenStreetMap's API to:

    * Download transportation networks for any country in the world
    * Import population information from WorldPop and Meta Data for Good sources
    * Create transportation zones and aggregate population into each zone
    * Import population by age and sex for any country in the world
    * Import amenities and building information to find more information on land-use
    * Estimate the rural population livin within two kilometers from an all-seasoned road


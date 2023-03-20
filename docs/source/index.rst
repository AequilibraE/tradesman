.. raw:: html

     <font size="18">
        Tradesman
     </font>

Tradesman is a package for building transport models from open data sources.
You can easily download network data from OpenStreetMap, import population, and
build zones. It downloads population pyramid data and amenities and building
information from OpenStreetMap and Microsoft, and builds synthetic populations
matching the target population pyramids.

Tradesman has been tightly integrated with a few data sources, and
while that allows for fast deployment for any region on Earth, it also makes it
somewhat complex to incorporate bespoke data sources. It is open-source though!

This is how easy one can build a model for Vietnam:

::

    from tradesman.model import Tradesman

    model_path
    project = Tradesman(model_path, "Vietnam")
    project.create()


Do you want to choose which steps to do?:

::

    from tradesman.model import Tradesman

    model_path
    project = Tradesman(model_path, "Detroit")

    project.import_model_area()
    project.add_country_borders()

    project.import_subdivisions(2) # imports 2 levels of political subdivisions below country (e.g. State & County)
    project.import_network()
    project.import_population()

    # The hexbin mesh to be created will have units with roughly 200m of side
    # And they will be clustered in zones with population between 500 and 10,000 people (tentatively)
    project.build_zoning(hexbin_size=200, max_zone_pop=10000, min_zone_pop=500, save_hexbins=False, overwrite=False)

    # We import the population pyramid for the modeled area into our zoning system
    project.import_pop_by_sex_and_age()

    project.build_population_synthesizer_data() # And create the synthetic population
    project.synthesize_population()

    # And we will not import amenities or building
    # project.import_amenities()
    # project.import_buildings(True)


.. raw:: html

     <font size="12">
        Contents
     </font>

.. sectnum::

.. toctree::
   :numbered:
   :maxdepth: 2

   build_analytics_model
   data_sources
   zoning
   synthetic_population
   _auto_examples/index

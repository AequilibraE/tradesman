Road Analytics
//////////////

The Road Analytics pipeline has been developed to implement the vision laid out
on `Geospatial Planning & Budgeting Platform (GPBP) Transport sector use cases
<https://docs.google.com/document/d/1AugI7_AiD2v-ES_actmseHsFMmi-oMdLxGF2YAcv5XY>`_.

Its main objective is to provide a set of tools that are:

1. Reproducible
2. Accessible
3. Cloud-capable
4. Easily-deployable
5. Accessible to non-programmers

And that provide capabilities for:

1. Generating visualizations of analytics models and its results
2. Estimating transport network demand based on Population and open-data PoI
3. Incorporating mobility data (vehicle GPS data and LBS)
4. A variety of use-cases
    * Fast summary statistics for transport networks
    * Network resilience to disruptions with respect to access to critical
      infrastructure
    * Descriptive population analytics
    * Rural Access Index (RAI)

This analytics pipeline is organized in sections for ease of use, and some
expertise in transportation planning/modelling/forecasting may be useful when
utilizing some of the more advanced analysis.

It is also noteworthy that this pipeline was designed to handle whole-of-country
data, mas little modification would be required to work only with sub-country
or even multi-country data.

Finally, the pipeline has been tightly integrated with a few data sources, and
while that allows for fast deployment for any region on Earth, it also makes it
somewhat complex to incorporate bespoke data sources.

Contents
--------
.. sectnum::

.. toctree::
   :numbered:
   :maxdepth: 2

   build_analytics_model
   data_sources
   travel_modelling
   concepts
   use_instructions

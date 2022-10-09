.. _use_instructions:

Using this software
===================


These Jupyter Notebooks can be run locally or in the Cloud (we recommend using
`SaturnCloud <https://saturncloud.io/>`_ , although Google Colab should be
powerful enough for very small countries), and we provide the documentation for
running it in both the Saturn Cloud and locally [TODO].

Saturn Cloud
------------

We have no association with Saturn Cloud whatsoever, but we have found their
cloud offering to be the most capable and user-friendly of all alternatives
currently on the market.

To set up Saturn Cloud, you should `sign up <https://saturncloud.io/>` first. If you do not have an account,
you should create one first, otherwise, you can just login. The next step is creating
a resource (aka environment) so we can execute the package. When setting up your
resource, make sure to include the following Python libs, otherwise we cannot assure
the complete functionality of the package.

* aequilibrae
* openmatrix
* geopandas
* pyarrow
* numpy v. 1.22.3
* folium
* rasterio
* rtree
* libpysal v. 4.3.0

Also, when setting up Saturn Cloud, it is possible to choose one of many disk spaces.
For most small countries, a 40 GB disk memory should be enough.

"Hidden functions"
------------------

Many of the steps and processes developed as part of this analytics pipeline
can be be either convoluted or technically complex (sometimes both), and that
has the potential of confusing users that are less comfortable with programming.

For this reason, we have removed all purely technical processes from the
Juypyter notebooks in favor of self-contained functions that accompany the
notebooks shipped with this analytics pipeline, but that the user can simply use
and not interact with, as they do with any Python library being used.

These "hidden functions" are organized inside the aptly named folder
*functions*, alongside the jupyter notebooks.

import os
import sys

from setuptools import setup, find_packages

sys.dont_write_bytecode = True

here = os.path.dirname(os.path.realpath(__file__))

pkgs = list(find_packages())

pkg_data = {
    "tradesman.data": ["population/*.csv"],
    "tradesman.model_creation": ["database_structure/*.*", "synthetic_population/controls_and_validation/*.csv"],
}
loose_modules = ["__version__"]

if __name__ == "__main__":
    reqs = [
        "rasterio",
        "matplotlib",
        "pycountry",
        "aequilibrae",
        "tabulate",
        "pysal",
    ]
    extra_reqs = {"all_features": ["osm2gmns", "populationsim >= 0.5.1", "dask_geopandas"]}
    setup(
        name="tradesman",
        version="0.2",
        install_requires=reqs,
        extra_requires=extra_reqs,
        packages=pkgs,
        package_dir={"": "."},
        py_modules=loose_modules,
        package_data=pkg_data,
        zip_safe=True,
        description="A friendly model builder for transportation models",
        author="Pedro Camargo, Renata Akemi",
        author_email="pedro@outerloop.io",
        url="https://github.com/AequilibraE/tradesman",
        classifiers=[
            "Programming Language :: Python",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
        ],
        cmdclass={},
        ext_modules=[],
    )

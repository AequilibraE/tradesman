import os
import sys

from setuptools import setup, find_packages

sys.dont_write_bytecode = True

here = os.path.dirname(os.path.realpath(__file__))

pkgs = [pkg for pkg in find_packages()]

pkg_data = {
    "tradesman.data": ["population/*.csv"],
    "tradesman.model_creation": ["database_structure/*.*", "synthetic_population/controls_and_validation/*.csv"],
}
loose_modules = ["__version__"]

if __name__ == "__main__":
    reqs = [
        "shapely>=2.0",
        "geopandas",
        "openmatrix",
        "rasterio",
        "matplotlib",
        "pycountry",
        "aequilibrae",
        "tabulate",
        "tqdm",
        "pysal",
    ]
    extra_reqs = {"all_features": ["osm2gmns >= 0.6.8", "populationsim >= 0.5.1", "dask_geopandas"]}
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
        author="Pedro Camargo, Renata Akemii",
        author_email="pedro@outerloop.io",
        url="https://github.com/AequilibraE/tradesman",
        classifiers=[
            "Programming Language :: Python",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
        ],
        cmdclass={},
        ext_modules=[],
    )

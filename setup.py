import os
import sys

from aequilibrae.paths.__version__ import release_version
from setuptools import setup, find_packages

sys.dont_write_bytecode = True

here = os.path.dirname(os.path.realpath(__file__))

pkgs = [pkg for pkg in find_packages()]

pkg_data = {"tradesman.data": ["population/*.csv"]}
loose_modules = []

if __name__ == "__main__":
    setup(
        name="aequilibrae",
        version=release_version,
        # TODO: Fix the requirements and optional requirements to bring directly from the requirements file
        install_requires=["pysal", "openmatrix", "rasterio", "matplotlib", "aequilibrae", "pyarrow"],
        packages=pkgs,
        package_dir={"": "."},
        py_modules=loose_modules,
        package_data=pkg_data,
        zip_safe=True,
        description="A friendly model builder for transportation models",
        author="Pedro Camargo",
        author_email="pedro@outerloop.io",
        url="https://github.com/AequilibraE/tradesman",
        license="See license.txt",
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

#!/usr/bin/env python
from setuptools import setup, find_packages
from setuptools.extension import Extension
from Cython.Build import cythonize


try:
    import numpy as np

    include_dirs = [np.get_include()]
except ImportError:
    include_dirs = []

extensions = cythonize(
    [
        Extension(
            "scrapely._htmlpage",
            ["scrapely/_htmlpage.pyx"],
            include_dirs=include_dirs,
        ),
        Extension(
            "scrapely.extraction._similarity",
            ["scrapely/extraction/_similarity.pyx"],
            include_dirs=include_dirs,
        ),
    ]
)

setup(
    name="sd-scrapely",
    version="0.13.5",
    license="BSD",
    description="A pure-python HTML screen-scraping library",
    author="Scrapy project",
    author_email="info@scrapy.org",
    url="https://github.com/SpazioDati/scrapely",
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Text Processing :: Markup :: HTML",
    ],
    install_requires=["numpy", "w3lib", "cython"],
    ext_modules=extensions,
)

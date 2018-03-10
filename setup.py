# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="py_d3",
    install_requires=["ipython"],
    packages=find_packages(),
    version="0.2.7",
    description="D3 block magic for Jupyter notebook.",
    author="Aleksey Bilogur",
    author_email="aleksey@residentmar.io",
    url="https://github.com/ResidentMario/py_d3",
    download_url="https://github.com/ResidentMario/py_d3/tarball/0.2.7",
    keywords=["data", "data visualization", "data analysis",
              "python", "jupyter", "ipython", "d3", "javascript"],
    classifiers = ["Framework :: IPython"],
    zip_safe = False,
)

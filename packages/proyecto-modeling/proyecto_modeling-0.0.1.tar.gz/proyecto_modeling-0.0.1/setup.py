# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="proyecto-modeling",
    version="0.0.1",
    description="Modeling phase package (CRISP-DM)",
    author="Angel Castellanos, Alejandro Azurdia, Diego Morales",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "proyecto-core==0.0.1",
        "scikit-learn>=1.0.0",
        "pandas>=2.0.0",
        "numpy>=1.20.0",
        "joblib>=1.2.0",
    ],
)

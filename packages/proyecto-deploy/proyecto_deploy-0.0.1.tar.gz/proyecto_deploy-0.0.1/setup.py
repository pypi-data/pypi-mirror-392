# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="proyecto-deploy",
    version="0.0.1",
    description="Deployment phase package (CRISP-DM)",
    author="Angel Castellanos, Alejandro Azurdia, Diego Morales",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "proyecto-core==0.0.1",
        "joblib>=1.2.0",
        "pandas>=2.0.0",
    ],
)

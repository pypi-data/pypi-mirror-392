# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="proyecto-du",
    version="0.0.1",
    description="Data Understanding phase package (CRISP-DM)",
    author="Angel Castellanos, Alejandro Azurdia, Diego Morales",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "proyecto-core==0.0.1",
        "pandas>=2.0.0",
        "pyyaml>=6.0",
    ],
)

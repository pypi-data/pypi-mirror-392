# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="proyecto-dp",
    version="0.0.1",
    description="Data Preparation phase package (CRISP-DM)",
    author="Angel Castellanos, Alejandro Azurdia, Diego Morales",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "proyecto-core==0.0.1",
        "pandas>=2.0.0",
        "nltk>=3.8",
        "spacy>=3.0.0",
    ],
)

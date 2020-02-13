# coding=utf-8
"""
author = jamon
"""

from setuptools import setup, find_packages

setup(
    name="obEspoir",
    version="0.1.0",
    keywords=("pip", "obEspoir", "game", "server", "frame", "distribute"),
    description="a distribute game frame",
    long_description="a distribute game frame",
    license="MIT Licence",

    url="https://gitee.com/jamon/obEspoir.git",
    author="jamon",
    author_email="jamonhe@foxmail.com",

    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=[],
    python_requires='>=3.6'
)
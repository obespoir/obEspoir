# coding=utf-8
"""
author = jamon
"""

import sys

from setuptools import setup, find_packages


if 2 > len(sys.argv):
    print("param error, please input 'python3 setup.py sdist bdist_wheel'")
    exit(0)


try:
    # Use setuptools if available, for install_requires (among other things).
    import setuptools
    from setuptools import setup
except ImportError:
    setuptools = None
    from distutils.core import setup


with open("obespoir/__init__.py") as f:
    ns = {}
    exec(f.read(), ns)
    version = ns["version"]

setup(
    name="obEspoir",
    version=version,
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
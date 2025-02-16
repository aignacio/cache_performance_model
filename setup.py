from setuptools import setup, find_packages, find_namespace_packages
import codecs
import os
from cache_performance_model.version import __version__

DESCRIPTION = "Cache performance model"
LONG_DESCRIPTION = "Simple cache model to evaluate performance between different topologies"

here = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

# Setting up
setup(
    name="cache_performance_model",
    packages=find_packages(),
    version=__version__,
    author="aignacio (Anderson Ignacio)",
    author_email="<anderson@aignacio.com>",
    license="MIT",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    url="https://github.com/aignacio/cache_performance_model",
    project_urls={
        "Bug Tracker": "https://github.com/aignacio/cache_performance_model/issues",
        "Source Code": "https://github.com/aignacio/cache_performance_model",
    },
    include_package_data=False,
    python_requires=">=3.6",
    install_requires=["numpy"],
    extras_require={
        "test": [
            "pytest",
        ],
    },
    keywords=["modeling", "cache", "hdl", "design"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
)

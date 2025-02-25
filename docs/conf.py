# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys


sys.path.insert(0, os.path.abspath("../cache_performance_model"))

def get_version():
    version_file = os.path.join(
        os.path.dirname(__file__), "../cache_performance_model/version.py"
    )
    with open(version_file) as f:
        for line in f:
            if line.startswith("__version__"):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")

project = 'Cache Performance Model'
copyright = '2025, Anderson Ignacio da Silva'
author = 'Anderson Ignacio da Silva'
version = get_version()
release = version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autosummary',
	'sphinx.ext.inheritance_diagram',
	'sphinx.ext.autosectionlabel',
	'sphinx_copybutton',
	'myst_parser',
]

source_suffix = {
	'.rst': 'restructuredtext',
	'.txt': 'markdown',
	'.md': 'markdown',
}

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
# html_theme = 'furo'
html_context = {
	"display_github": True,
	"github_user": "aignacio",
	"github_repo": "cache_performance_model",
	"github_version": "master",
	"conf_py_path": "/docs/",
}

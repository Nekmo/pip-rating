# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import sys
import os
import setuptools  # noqa: F401

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'pip-rating'
copyright = '2023, Nekmo'
author = 'Nekmo'

directory = os.path.dirname(__file__)
cwd = os.getcwd()
project_root = os.path.dirname(cwd)

# Insert the project root dir as the first element in the PYTHONPATH.
# This lets us ensure that the source package is imported, and that its
# version is used.
sys.path.insert(0, project_root)

import pip_rating

# The version info for the project you're documenting, acts as replacement
# for |version| and |release|, also used in various other places throughout
# the built documents.
#
# The short X.Y version.
version = pip_rating.__version__
# The full version, including alpha/beta/rc tags.
release = pip_rating.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.viewcode', 'sphinx_click.ext']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

html_theme_options = {
    'logo': 'logo.png',
    'description': 'Are the dependencies (and their dependencies) of your project secure and maintained?',
    'github_user': 'Nekmo',
    'github_repo': 'pip-rating',
    'github_type': 'star',
    'github_banner': "forkme_right_darkblue_121621.png",
    'travis_button': False,
    'codecov_button': True,
    'analytics_id': 'UA-62276079-1',
    'canonical_url': 'http://docs.nekmo.org/pip-rating/'
}

html_css_files = [
    '_static/custom.css',
]

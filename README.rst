.. image:: https://img.shields.io/github/actions/workflow/status/Nekmo/pip-rating/test.yml?style=flat-square&maxAge=2592000&branch=master
  :target: https://github.com/Nekmo/pip-rating/actions?query=workflow%3ATests
  :alt: Latest Tests CI build status

.. image:: https://img.shields.io/pypi/v/pip-rating.svg?style=flat-srating
  :target: https://pypi.org/project/requirements-srating
  :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/pyversions/pip-rating.svg?style=flat-srating
  :target: https://pypi.org/project/requirements-srating
  :alt: Python versions

.. image:: https://img.shields.io/codeclimate/github/Nekmo/pip-rating.svg?style=flat-srating
  :target: https://codeclimate.com/github/Nekmo/pip-rating
  :alt: Code Climate

.. image:: https://img.shields.io/codecov/c/github/Nekmo/pip-rating/master.svg?style=flat-srating
  :target: https://codecov.io/github/Nekmo/pip-rating
  :alt: Test coverage


##########
pip-rating
##########

**Are the 📦 dependencies (and their dependencies) of your project secure and maintained?**


To **install 🔧 pip-rating**, run this command in your terminal (in a virtualenv preferably):

.. code-block:: console

    $ pip install pip-rating

This is the preferred method to install pip-rating, as it will always install the most recent stable release.
If you don't have `pip <https://pip.pypa.io>`_ installed, this
`Python installation guide <http://docs.python-guide.org/en/latest/starting/installation/>`_ can guide you through
the process. 🐍 **Python 3.7-3.11** are tested and supported.

Usage
=====
To check the dependencies of your project (pip-rating will detect your requirements file automatically) run this
command in your project root:

.. code-block:: console

    $ pip-rating

To check the dependencies of a specific requirements file (pip-rating supports the files *requirements.txt*,
*requirements.in*, *setup.py*, *setup.cfg*, *pyproject.toml* & *Pipfile*), run this command:

.. code-block:: console

    $ pip-rating analyze-file <requirements_file>


Features
========

* TODO


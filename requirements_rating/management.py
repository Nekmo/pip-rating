# -*- coding: utf-8 -*-

"""Console script for requirements-rating."""
import os

import click
from pip._internal.locations import USER_CACHE_DIR

from requirements_rating.requirements import Requirements


@click.group()
def cli():
    """Console script for requirements-rating."""
    pass


def common_options(function):
    function = click.option(
        "--cache-dir",
        envvar="PIP_CACHE_DIR",
        type=click.Path(exists=False, file_okay=False, dir_okay=True, resolve_path=True),
        default=os.path.join(USER_CACHE_DIR, "wheels", "pipgrip"),
        help="Use a custom cache dir.",
    )(function)
    function = click.option(
        "--index-url",
        # envvar="PIP_INDEX_URL",  # let pip discover
        # default="https://pypi.org/simple",
        help="Base URL of the Python Package Index (default https://pypi.org/simple).",
    )(function)
    function = click.option(
        "--extra-index-url",
        # envvar="PIP_EXTRA_INDEX_URL",  # let pip discover
        help="Extra URLs of package indexes to use in addition to --index-url.",
    )(function)
    return function


@cli.command()
@click.argument('requirements_file', type=click.Path(exists=True))
@common_options
def analyze_file(requirements_file: str, cache_dir: str, index_url: str, extra_index_url: str):
    requirements = Requirements(requirements_file, cache_dir, index_url, extra_index_url)
    packages = requirements.get_packages()
    score = list(packages.values())[0].rating.global_rating_score
    pass


@cli.command()
@click.argument('package_name')
@common_options
def analyze_package(package_name: str, cache_dir: str, index_url: str, extra_index_url: str):
    requirements = Requirements(None, cache_dir, index_url, extra_index_url)
    package = requirements.get_package(package_name)
    score = package.rating.global_rating_score
    pass


if __name__ == '__main__':
    cli()

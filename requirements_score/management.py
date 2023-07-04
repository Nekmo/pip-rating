# -*- coding: utf-8 -*-

"""Console script for requirements-score."""
import os

import click
from pip._internal.locations import USER_CACHE_DIR

from requirements_score.requirements import Requirements


@click.command()
@click.argument('requirements_file', type=click.Path(exists=True))
@click.option(
    "--cache-dir",
    envvar="PIP_CACHE_DIR",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, resolve_path=True),
    default=os.path.join(USER_CACHE_DIR, "wheels", "pipgrip"),
    help="Use a custom cache dir.",
)
@click.option(
    "--index-url",
    # envvar="PIP_INDEX_URL",  # let pip discover
    # default="https://pypi.org/simple",
    help="Base URL of the Python Package Index (default https://pypi.org/simple).",
)
@click.option(
    "--extra-index-url",
    # envvar="PIP_EXTRA_INDEX_URL",  # let pip discover
    help="Extra URLs of package indexes to use in addition to --index-url.",
)
def manage(requirements_file: str, cache_dir: str, index_url: str, extra_index_url: str):
    requirements = Requirements(requirements_file, cache_dir, index_url, extra_index_url)
    packages = requirements.get_packages()
    score = list(packages.values())[0].rating.global_rating_score
    pass


# Uncomment it to use subcommands:
#
# @click.group()
# @click.option('--debug/--no-debug', default=False)
# def cli(debug):
#     click.echo(f"Debug mode is {'on' if debug else 'off'}")
#
# @cli.command()  # @cli, not @click!
# def sync():
#     click.echo('Syncing')


if __name__ == '__main__':
    manage()

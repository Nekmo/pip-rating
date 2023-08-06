#!/usr/bin/env python3
"""
This file is used for INTERNAL PURPOSES. It is not part of the component.
_action.py is used by action.yml for run the GitHub Action. This outputs
the rating of the requirements file and optionally creates a badge.
"""
import warnings

# Force patch of distutils, which is vendored into setuptools
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import setuptools  # noqa:F401
    import pip  # noqa:F401

import os
from pathlib import Path
from typing import Optional, List

import click

from pip_rating.dependencies import Dependencies
from pip_rating.management import common_options
from pip_rating.req_files import get_req_file_cls, REQ_FILE_CLASSES, find_in_directory
from pip_rating.results import Results


PIP_RATING_IGNORE_PACKAGES = os.environ.get("PIP_RATING_IGNORE_PACKAGES", "").split(" ")


@click.command()
@click.option("--file", type=click.Path(exists=False, dir_okay=False), default="")
@click.option(
    "--file-type", type=click.Choice(list(REQ_FILE_CLASSES.keys()) + [""]), default=""
)
@click.option("--badge-path", type=click.Path(exists=False, dir_okay=False), default="")
@common_options
def action(
    file: Optional[str],
    file_type: Optional[str],
    badge_path: Optional[str],
    cache_dir: str,
    index_url: str,
    extra_index_url: str,
    format_name: str,
    to_file: Optional[str],
    ignore_packages: List[str],
):
    if not file:
        file = str(find_in_directory(Path.cwd()).path)
    results = Results(to_file)
    file = Path(file)
    if not file_type:
        req_file_cls = get_req_file_cls(file)
    else:
        req_file_cls = REQ_FILE_CLASSES[file_type]
    if not ignore_packages:
        ignore_packages = PIP_RATING_IGNORE_PACKAGES
    dependencies = Dependencies(
        results,
        req_file_cls(file),
        cache_dir,
        index_url,
        extra_index_url,
        ignore_packages=ignore_packages,
    )
    results.show_results(dependencies, format_name)
    if badge_path:
        results = Results(badge_path)
        results.show_badge_results(dependencies)


if __name__ == "__main__":
    action()

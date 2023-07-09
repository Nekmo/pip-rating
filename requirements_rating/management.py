# -*- coding: utf-8 -*-
"""Console script for requirements-rating."""
import os
from pathlib import Path
from typing import Optional, List

import click
from rich.console import Console

from requirements_rating._compat import USER_CACHE_DIR
from requirements_rating.dependencies import Dependencies
from requirements_rating.exceptions import catch
from requirements_rating.req_files import get_req_file_cls, REQ_FILE_CLASSES, find_in_directory
from requirements_rating.req_files.package_list import PackageList
from requirements_rating.results import Results


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx: click.Context):
    """Console script for requirements-rating."""
    if ctx.invoked_subcommand is None:
        req_file = find_in_directory(Path.cwd())
        Console().print(f"Autodetected requirements file: [bold green]{req_file}[/bold green]")
        ctx.invoke(analyze_file, file=str(req_file.path))


def common_options(function):
    function = click.option(
        "--cache-dir",
        envvar="PIP_CACHE_DIR",
        type=click.Path(exists=False, file_okay=False, dir_okay=True, resolve_path=True),
        default=os.path.join(USER_CACHE_DIR, "wheels", "requirements-rating"),
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
    function = click.option(
        "--format",
        "-f",
        "format_name",
        # envvar="PIP_EXTRA_INDEX_URL",  # let pip discover
        default="text",
        help="Extra URLs of package indexes to use in addition to --index-url.",
    )(function)
    return function


@cli.command()
@click.argument('file', type=click.Path(exists=True, dir_okay=False))
@click.option('--file-type', type=click.Choice(list(REQ_FILE_CLASSES.keys())), default=None)
@common_options
def analyze_file(file: str, file_type: Optional[str], cache_dir: str, index_url: str, extra_index_url: str,
                 format_name: str):
    results = Results()
    file = Path(file)
    if file_type is None:
        req_file_cls = get_req_file_cls(file)
    else:
        req_file_cls = REQ_FILE_CLASSES[file_type]
    results.status.update(f"Read requirements file [bold green]{file}[/bold green]")
    dependencies = Dependencies(results, req_file_cls(file), cache_dir, index_url, extra_index_url)
    results.show_results(dependencies, format_name)


@cli.command()
@click.argument('package_names', nargs=-1, required=True)
@common_options
def analyze_package(package_names: List[str], cache_dir: str, index_url: str, extra_index_url: str, format_name: str):
    results = Results()
    req_file = PackageList(package_names)
    dependencies = Dependencies(results, req_file, cache_dir, index_url, extra_index_url)
    if len(package_names) == 1:
        nodes = dependencies.dependencies_tree.children[0].children
        packages = PackageList(list(package_names) + [f"{node.name}=={node.version}" for node in nodes])
        dependencies = Dependencies(results, packages, cache_dir, index_url, extra_index_url)
    results.show_results(dependencies, format_name)


if __name__ == '__main__':
    catch(cli)()

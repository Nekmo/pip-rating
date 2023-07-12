# -*- coding: utf-8 -*-
"""Console script for pip-rating."""
import os
import platform
import sys
from pathlib import Path
from typing import Optional, List

import click
import requests
from requests import RequestException
from rich.console import Console
from pkg_resources import parse_version

import pip_rating
from pip_rating import project_name, __version__
from pip_rating._compat import USER_CACHE_DIR
from pip_rating.dependencies import Dependencies
from pip_rating.exceptions import catch
from pip_rating.req_files import get_req_file_cls, REQ_FILE_CLASSES, find_in_directory
from pip_rating.req_files.package_list import PackageList
from pip_rating.results import Results, FORMATS


def is_last_version() -> Optional[bool]:
    try:
        with requests.get(f"https://pypi.org/pypi/{project_name}/json") as response:
            response.raise_for_status()
            return parse_version(__version__) >= parse_version(response.json()["info"]["version"])
    except RequestException:
        return None


@click.group(invoke_without_command=True)
@click.option("--version", "-v", is_flag=True, help="Show version and exit.")
@click.pass_context
def cli(ctx: click.Context, version: bool):
    """Are the dependencies (and their dependencies) of your project secure and maintained?
    Running this command without arguments detects the dependencies file of your project
    (it supports *requirements.in, requirements.txt, setup.py, setup.cfg, Pipenv and pyproject.toml*)
    and analyzes it.

    If your file is not detected (or you want to parse another file, like your development dependencies)
    you can use the ``analyze-file`` command.
    """
    if version:
        latest_version = is_last_version()
        console = Console()
        console.print(f"[bold]{project_name}[/bold] [bold green]{__version__}[/bold green]")
        console.print(
            "  :top_arrow: This is the latest version." if latest_version
    else f"  :boom: There is a newer version available. Update it using 'pip install -U {project_name}'"
        )
        console.print(f"  :snake: Python version: {sys.version.split()[0]}")
        console.print(f"  :computer: Platform: [bold blue]{platform.platform()}[/bold blue]")
        console.print(f"  :package: Installation path: {os.path.dirname(pip_rating.__file__)}")
        console.print(f"  :file_folder: Current path: {os.getcwd()}")
        ctx.exit(0)
    elif ctx.invoked_subcommand is None:
        req_file = find_in_directory(Path.cwd())
        Console().print(f"Autodetected requirements file: [bold green]{req_file}[/bold green]")
        ctx.invoke(analyze_file, file=str(req_file.path))


def common_options(function):
    function = click.option(
        "--cache-dir",
        envvar="PIP_CACHE_DIR",
        type=click.Path(exists=False, file_okay=False, dir_okay=True, resolve_path=True),
        default=os.path.join(USER_CACHE_DIR, "wheels", "pip-rating"),
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
        type=click.Choice(FORMATS),
        # envvar="PIP_EXTRA_INDEX_URL",  # let pip discover
        default="text",
        help=f"Output format. Supported formats: {', '.join(FORMATS)}. By default it uses 'text'.",
    )(function)
    return function


@cli.command()
@click.argument('file', type=click.Path(exists=True, dir_okay=False))
@click.option('--file-type', type=click.Choice(list(REQ_FILE_CLASSES.keys())), default=None)
@common_options
def analyze_file(file: str, file_type: Optional[str], cache_dir: str, index_url: str, extra_index_url: str,
                 format_name: str):
    """Analyze a requirements file. A requirements file is required as argument. By default, it tries to detect the
    type of the file, but you can force it using the ``--file-type`` option. The supported file types are:
    *requirements.txt, requirements.in, setup.py, setup.cfg, Pipfile and pyproject.toml*.
    """
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
    """Analyze a package. A package name is required as argument. The syntax is the same as pip install. For example:
    ``Django==4.2.3``. If only one package is specified, it will show their dependencies in detail.
    """
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

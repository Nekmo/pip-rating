# -*- coding: utf-8 -*-

"""Console script for requirements-score."""
import click


@click.command()
# @click.argument('<arg>')
def manage():
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

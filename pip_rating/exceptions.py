# -*- coding: utf-8 -*-

"""Exceptions for pip-rating."""
import sys

from rich.console import Console


class RequirementsRatingError(Exception):
    body = ''
    exit_code = 10

    def __init__(self, extra_body=''):
        self.extra_body = extra_body

    def __str__(self):
        msg = self.__class__.__name__
        if self.body:
            msg += ': {}'.format(self.body)
        if self.extra_body:
            msg += ('. {}' if self.body else ': {}').format(self.extra_body)
        return msg


class RequirementsRatingParseError(RequirementsRatingError):
    exit_code = 11


class RequirementsRatingInvalidFile(RequirementsRatingError):
    exit_code = 12


class RequirementsRatingMissingReqFile(RequirementsRatingError):
    exit_code = 13

    def __init__(self, directory: str):
        self.directory = directory
        super().__init__(f"Missing requirements file in {directory}")


def catch(fn):
    def wrap(*args, **kwargs):
        console = Console(stderr=True)
        try:
            fn(*args, **kwargs)
        except RequirementsRatingMissingReqFile as e:
            command = sys.argv[0].split('/')[-1]
            console.print(
                ":exclamation:  Requirements file not found in [bold orange1]{}[/bold orange1]".format(e.directory)
            )
            console.print(
                ":information:  You can specify the requirements file using "
                f"\"[bold]{command} analyze-file --req-file [grey53]<requirements_file>[/grey53][/bold]\"",
                highlight=False
            )
            sys.exit(e.exit_code)
        except RequirementsRatingError as e:
            sys.stderr.write('[Error] pip-rating Exception:\n{}\n'.format(e))
            sys.exit(e.exit_code)
    return wrap

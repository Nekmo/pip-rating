#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `requirements_score` package."""


import unittest
from click.testing import CliRunner

from requirements_score import requirements_score
from requirements_score import cli


class TestRequirements_score(unittest.TestCase):
    """Tests for `requirements_score` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'requirements_score.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output

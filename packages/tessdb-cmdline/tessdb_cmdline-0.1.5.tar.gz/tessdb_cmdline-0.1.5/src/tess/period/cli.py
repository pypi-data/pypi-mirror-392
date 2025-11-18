# ----------------------------------------------------------------------
# Copyright (c) 2024 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------

# --------------------
# System wide imports
# -------------------

import csv
import logging
import functools
from argparse import ArgumentParser, Namespace

# -------------------
# Third party imports
# -------------------

from lica.asyncio.cli import execute

# --------------
# local imports
# -------------

from .._version import __version__
from . import parser as prs
from .mqtt import subscriber

# ---------
# Constants
# ---------


# ----------------
# Global variables
# ----------------

log = logging.getLogger(__name__.split(".")[-1])

# ================
# MAIN ENTRY POINT
# ================


async def cli_period_estimate(args: Namespace) -> None:
    await subscriber(args.name, args.num_samples)


def add_args(parser: ArgumentParser) -> None:
    subparser = parser.add_subparsers(dest="command", required=True)
    p = subparser.add_parser(
        "estimate",
        parents=[prs.phot()],
        help="Estimate photomter Tx period",
    )
    p.set_defaults(func=cli_period_estimate)


async def cli_main(args: Namespace) -> None:
    await args.func(args)


def main():
    execute(
        main_func=cli_main,
        add_args_func=add_args,
        name=__name__,
        version=__version__,
        description="TESSDB Tx period estimation tool",
    )

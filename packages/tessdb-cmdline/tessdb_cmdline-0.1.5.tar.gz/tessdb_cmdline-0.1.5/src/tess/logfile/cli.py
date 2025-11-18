# ----------------------------------------------------------------------
# Copyright (c) 2024 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------

# --------------------
# System wide imports
# -------------------

import os
import csv
import logging

from argparse import ArgumentParser, Namespace

# -------------------
# Third party imports
# -------------------

from lica.cli import execute
from lica.sqlalchemy import sqa_logging

# --------------
# local imports
# -------------

from .._version import __version__
from . import parser as prs
from .dao import engine_tdb, engine_zpt
from .logfile import collect_readings_for, collect_references

# ----------------
# Global variables
# ----------------

package = ".".join(__name__.split(".")[:-1])
log = logging.getLogger(__name__.split(".")[-1])

# ================
# MAIN ENTRY POINT
# ================


def cli_readings(args: Namespace) -> None:
    readings = collect_readings_for(args.name, args.log_dir, args.start, args.end, args.batch_size)
    if readings:
        log.info("start = %s, end = %s", readings[0]["tstamp"], readings[-1]["tstamp"])
        register_tstamp = readings[0]["tstamp"].replace(hour=0, minute=0, second=0, microsecond=0)
        log.info("Should register photometer at %s", register_tstamp)
        start = readings[0]["tstamp"].strftime("%Y%m%d")
        end = readings[-1]["tstamp"].strftime("%Y%m%d")
        output_path, ext = os.path.splitext(args.output_file)
        dire = os.path.dirname(output_path)
        base = os.path.basename(output_path)
        base = f"{base}_{start}_{end}{ext}"
        output_path = os.path.join(dire, base)
        with open(output_path, "w", newline="") as csvfile:
            fieldnames = readings[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=",")
            writer.writeheader()
            for item in readings:
                writer.writerow(item)
        log.info("readings written to %s", output_path)
    else:
        log.info("No readings found in the [%s - %s] period", args.start, args.end)



def cli_names(args: Namespace) -> None:
    summary_info, registry_info = collect_references(args.log_dir, args.start, args.end)
    with open(args.output_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter="\t")
        writer.writerow(("name",  "#readings", "month", "from", "to", "registered?", "details"))
        for item in summary_info:
            writer.writerow(item)
    with open(args.registry_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        writer.writerow(("tstamp", "name", "mac", "model", "firmware", "zp1", "zp2", "zp3", "zp4", "place", "obs_type", "obs_name"))
        for item in registry_info:
            writer.writerow(item)


def add_args(parser: ArgumentParser) -> None:
    subparser = parser.add_subparsers(dest="command", required=True)
    p = subparser.add_parser(
        "readings",
        parents=[prs.name(), prs.logdir(), prs.ofile(), prs.batch(), prs.range()],
        help="Recover single photometer readings",
    )
    p.set_defaults(func=cli_readings)
    p = subparser.add_parser(
        "names",
        parents=[
            prs.logdir(),
            prs.ofile(),
            prs.rfile(),
            prs.range(),
        ],
        help="List photometers with recoverable readings",
    )
    p.set_defaults(func=cli_names)


def cli_main(args: Namespace) -> None:
    sqa_logging(args)
    args.func(args)
    engine_zpt.dispose()
    engine_tdb.dispose()


def main():
    execute(
        main_func=cli_main,
        add_args_func=add_args,
        name=__name__,
        version=__version__,
        description="TESSDB Log file readings recovery tool",
    )

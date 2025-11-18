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
from itertools import batched, islice
from argparse import ArgumentParser, Namespace
from typing import Iterable, Dict, Any, List

# -------------------
# Third party imports
# -------------------

import decouple

from pydantic import ValidationError

from lica.cli import execute
from lica.jinja2 import render_from
from lica.sqlalchemy import sqa_logging

from tessdbdao import RegisterState, ReadingSource, TimestampSource
from tessdbapi.model import PhotometerInfo, ReadingInfo1c, ReadingInfo4c, ReadingInfo
from tessdbapi.noasync.photometer.register import (
    photometer_register,
    photometer_assign,
    photometer_fix_valid_since,
)
from tessdbapi.noasync.photometer.reading import photometer_batch_write

# --------------
# local imports
# -------------

from .._version import __version__
from . import parser as prs
from .dao import engine, Session
from ..admin import TessDbServer

# ----------------
# Global variables
# ----------------

package = ".".join(__name__.split(".")[:-2])
log = logging.getLogger(__name__.split(".")[-1])


host = decouple.config("TESSDB_ADMIN_HOST", default="localhost")
port = decouple.config("TESSDB_ADMIN_PORT", cast=int, default=8080)


CREATE_TEMPLATE = "photometer_register.sh.j2"

# ----------------
# Global variables
# ----------------


render = functools.partial(render_from, package)


def build_pydantic_models(batch: Iterable[Dict[str, Any]], every: int) -> List[ReadingInfo]:
    readings = list()
    for row in islice(batch, 0, None, every):
        if "freq4" not in row:
            readings.append(
                ReadingInfo1c(
                    tstamp=row["tstamp"],
                    tstamp_src=row.get("tstamp_src", TimestampSource.SUBSCRIBER),
                    name=row["name"],
                    sequence_number=row["sequence_number"],
                    box_temperature=row["box_temperature"],
                    sky_temperature=row["sky_temperature"],
                    signal_strength=row["signal_strength"],
                    hash=row.get("hash"),
                    freq1=row["freq1"],
                    mag1=row["mag1"],
                )
            )
        else:
            readings.append(
                ReadingInfo4c(
                    tstamp=row["tstamp"],
                    tstamp_src=row.get("tstamp_src", TimestampSource.SUBSCRIBER),
                    name=row["name"],
                    sequence_number=row["sequence_number"],
                    box_temperature=row["box_temperature"],
                    sky_temperature=row["sky_temperature"],
                    signal_strength=row["signal_strength"],
                    hash=row.get("hash"),
                    freq1=row["freq1"],
                    mag1=row["mag1"],
                    freq2=row["freq2"],
                    mag2=row["mag2"],
                    freq3=row["freq3"],
                    mag3=row["mag3"],
                    freq4=row["freq4"],
                    mag4=row["mag4"],
                )
            )
    return readings


# ================
# MAIN ENTRY POINT
# ================


def cli_photom_generate(args: Namespace) -> None:
    with open(args.input_csv, newline="") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        photometers = [dict(row) for row in reader]
        log.info("Number of candidate photometers to register: %d", len(photometers))
        photometers = list(
            filter(
                lambda x: all(
                    [
                        x["firmware"],
                    ]
                ),
                photometers,
            )
        )
        log.info(
            "Number of candidate photometers to register after filtering: %d", len(photometers)
        )
        context = {"photometers": photometers}
        script = render(CREATE_TEMPLATE, context)
        with open(args.output_script, "w") as outfile:
            outfile.write(script)
        log.info("script '%s' generated", args.output_script)


def cli_photom_register(args: Namespace) -> None:
    try:
        candidate = PhotometerInfo(
            name=args.name,
            mac_address=args.mac_address,
            model=args.model,
            firmware=args.firmware,
            authorised=args.authorise,
            registered=RegisterState.MANUAL,
            zp1=args.zp1,
            filter1=args.filter1,
            offset1=args.offset1,
            zp2=args.zp2,
            filter2=args.filter2,
            offset2=args.offset2,
            zp3=args.zp3,
            filter3=args.filter3,
            offset3=args.offset3,
            zp4=args.zp4,
            filter4=args.filter4,
            offset4=args.offset4,
            tstamp=args.timestamp,
        )
    except ValidationError as e:
        log.error("Validation Error")
        log.info(e)
    else:
        with TessDbServer(host=host, port=port, test=args.test):
            with Session() as session:
                with session.begin():
                    log.info("Registering photometer: %s", dict(candidate))
                    photometer_register(
                        session,
                        candidate=candidate,
                        place=args.place,
                        observer_name=args.observer,
                        observer_type=args.type,
                        dry_run=args.dry_run,
                    )


def cli_photom_upload(args: Namespace) -> None:
    name = args.input_csv.split("_")[0]
    with open(args.input_csv) as csvfile:
        reader = csv.DictReader(csvfile)
        with TessDbServer(host=host, port=port, test=args.test):
            with Session() as session:
                for i, batch in enumerate(batched(reader, args.batch_size * args.every), start=1):
                    log.info(
                        "[%s] Writing batch #%d with %d samples, decimated to %d samples",
                        name,
                        i,
                        len(batch),
                        len(batch) // args.every,
                    )
                    subsampled = build_pydantic_models(batch, args.every)
                    photometer_batch_write(
                        session=session,
                        readings=subsampled,
                        auth_filter=False,
                        latest=False,
                        source=ReadingSource.IMPORTED,
                        dry_run=args.dry_run,
                    )


def cli_photom_assign(args: Namespace) -> None:
    with TessDbServer(host=host, port=port, test=args.test):
        with Session() as session:
            with session.begin():
                photometer_assign(
                    session=session,
                    phot_name=args.name,
                    place=args.place,
                    observer_name=args.observer,
                    observer_type=args.type,
                    update_readings=args.readings,
                    update_readings_since=args.since,
                    update_readings_until=args.until,
                    dry_run=args.dry_run,
                )


def cli_photom_valid_since(args: Namespace) -> None:
    with TessDbServer(host=host, port=port, test=args.test):
        with Session() as session:
            with session.begin():
                photometer_fix_valid_since(
                    session=session,
                    name=args.name,
                    valid_since=args.timestamp,
                    dry_run=args.dry_run,
                )


def add_args(parser: ArgumentParser) -> None:
    subparser = parser.add_subparsers(dest="command", required=True)
    p = subparser.add_parser(
        "register",
        parents=[prs.tstamp(), prs.photom(), prs.location(), prs.observer(), prs.dry(), prs.test()],
        help="Register a new photometer",
    )
    p.set_defaults(func=cli_photom_register)
    p = subparser.add_parser(
        "valid_since",
        parents=[prs.name(), prs.tstamp(), prs.dry(), prs.test()],
        help="fix valid_since in an already registered photometer",
    )
    p.set_defaults(func=cli_photom_valid_since)
    p = subparser.add_parser(
        "assign",
        parents=[prs.name(), prs.location(), prs.observer(), prs.readings(), prs.dry(), prs.test()],
        help="Assign a location and observer to a given photometer",
    )
    p.set_defaults(func=cli_photom_assign)
    p = subparser.add_parser(
        "generate",
        parents=[prs.ifile(), prs.ofile(), prs.dry()],
        help=("Generate photometers register script from photometers CSV",),
    )
    p.set_defaults(func=cli_photom_generate)
    p = subparser.add_parser(
        "upload",
        parents=[prs.ifile(), prs.batch(), prs.every(), prs.dry(), prs.test()],
        help=("Upload readings to database"),
    )
    p.set_defaults(func=cli_photom_upload)


def cli_main(args: Namespace) -> None:
    sqa_logging(args)
    args.func(args)
    engine.dispose()


def main():
    execute(
        main_func=cli_main,
        add_args_func=add_args,
        name=__name__,
        version=__version__,
        description="TESSDB Observer tool",
    )

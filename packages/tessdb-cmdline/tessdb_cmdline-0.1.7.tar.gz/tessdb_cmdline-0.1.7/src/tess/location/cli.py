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
from collections import defaultdict
from argparse import ArgumentParser, Namespace

# -------------------
# Third party imports
# -------------------

import decouple

from lica.cli import execute
from lica.tabulate import paging
from lica.jinja2 import render_from
from lica.sqlalchemy import sqa_logging


from tessdbapi.model import LocationInfo 
from tessdbapi.noasync.location import location_create, location_update, location_nearby, location_list
from tessdbapi.location_common import geolocate, geolocate_raw

# --------------
# local imports
# -------------

from .._version import __version__
from . import parser as prs
from .dao import engine, Session
from ..admin import TessDbServer

# ---------
# Constants
# ---------

CREATE_TEMPLATE = "location_create.sh.j2"

# ----------------
# Global variables
# ----------------

log = logging.getLogger(__name__.split(".")[-1])
package = ".".join(__name__.split(".")[:-2])

render = functools.partial(render_from, package)

host = decouple.config("TESSDB_ADMIN_HOST", default="localhost")
port = decouple.config("TESSDB_ADMIN_PORT", cast=int, default=8080)

# ================
# MAIN ENTRY POINT
# ================

def cli_reverse_lookup(args: Namespace) -> None:
    if args.raw:
        result = geolocate_raw(args.longitude, args.latitude)
    else:
        result = geolocate(args.longitude, args.latitude)
    result = [tup for tup in result.items()]
    paging(result, headers=("Name", "Value"), table_fmt="grid")


def cli_location_generate(args: Namespace) -> None:
    with open(args.input_csv, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        locations = [dict(row) for row in reader]
    log.info("found %d records", len(locations))
    loc_by_place = defaultdict(list)
    for obs in locations:
        loc_by_place[(obs["longitude"],obs["latitude"])].append(obs)
    for key, val in loc_by_place.items():
        if len(val) > 1 and key != ("",""):
            log.warning("Duplicate coordinate entries: %s", val)
        elif len(val) > 1 and key == ("",""):
            log.warning("Missing coordinate for %d entries", len(val))
    locations = [val[0] for key, val in loc_by_place.items() if key != ("","")]
    log.info("reduced to %d locations", len(locations))
    context = {"locations": locations}
    script = render(CREATE_TEMPLATE, context)
    with open(args.output_script, "w") as outfile:
        outfile.write(script)
    log.info("script '%s' generated", args.output_script)



def cli_location_create(args: Namespace) -> None:
    candidate = LocationInfo(
        longitude=args.longitude,
        latitude=args.latitude,
        height=args.height,
        place=args.place.strip() if args.place else None,
        town=args.town.strip() if args.town else None,
        sub_region=args.sub_region.strip() if args.sub_region else None,
        region=args.region.strip() if args.region else None,
        country=args.country.strip() if args.country else None,
        timezone=args.timezone.strip() if args.timezone else None,
    )
    with TessDbServer(host=host, port=port, test=args.test):
        with Session() as session:
            with session.begin():
                log.info("Registering location: %s", dict(candidate))
                if args.nearby is not None:
                    nearby_locs = location_nearby(session, candidate, limit=args.nearby)
                    if nearby_locs:
                        log.warning("Stopping here. New location is nearby these locations:")
                        for loc in nearby_locs:
                            log.warning(loc)
                        return
                location = location_create(
                    session,
                    candidate,
                    args.dry_run,
                )
            if location is not None:
                session.refresh(location)
                log.info(location)

def cli_location_update(args: Namespace) -> None:
    candidate = LocationInfo(
        longitude=args.longitude,
        latitude=args.latitude,
        height=args.height,
        place=args.place,
        town=args.town,
        sub_region=args.sub_region,
        region=args.region,
        country=args.country,
        timezone=args.timezone,
    )
    with TessDbServer(host=host, port=port, test=args.test):
        with Session() as session:
            with session.begin():
                log.info("Updating location: %s", dict(candidate))
                location_update(
                    session,
                    candidate,
                    args.dry_run,
                )

def cli_location_list(args: Namespace) -> None:
    with TessDbServer(host=host, port=port, test=args.test):
        with Session() as session:
            with session.begin():
                locations = location_list(session)
                locations = [ dict(location.__dict__) for location in locations]
                for location in locations:
                    del location["_sa_instance_state"]
                headers = locations[0].keys()
                result = [tup for tup in locations.items()]
                paging(result, headers=headers, table_fmt="grid")


def add_args(parser: ArgumentParser) -> None:
    subparser = parser.add_subparsers(dest="command", required=True)
    p = subparser.add_parser(
        "create",
        parents=[prs.coords(), prs.place(), prs.nominatim(), prs.nearby(), prs.dry(), prs.test()],
        help="Create new location",
    )
    p.set_defaults(func=cli_location_create)
    p = subparser.add_parser(
        "update",
        parents=[prs.coords(), prs.place(), prs.nominatim(), prs.dry(), prs.test()],
        help="Update existing location",
    )
    p.set_defaults(func=cli_location_update)
    p = subparser.add_parser(
        "reverse",
        parents=[prs.coords(),  prs.raw()],
        help="Location Reverse lookup operation",
    )
    p.set_defaults(func=cli_reverse_lookup)
    p = subparser.add_parser(
        "generate",
        parents=[
            prs.ifile(),
            prs.ofile(),
            prs.dry(),
        ],
        help="Generate location creation script from observers CSV",
    )
    p.set_defaults(func=cli_location_generate)
    p = subparser.add_parser(
        "list",
        parents=[prs.test()],
        help="List locations in database",
    )
    p.set_defaults(func=cli_location_list)


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
        description="TESSDB Location tool",
    )

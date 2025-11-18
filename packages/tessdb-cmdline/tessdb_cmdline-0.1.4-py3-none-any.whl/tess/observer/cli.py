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
# -------------------º

import decouple

from lica.cli import execute
from lica.jinja2 import render_from
from lica.sqlalchemy import sqa_logging

from tessdbdao import ObserverType
from tessdbapi.model import ObserverInfo
from tessdbapi.noasync.observer import observer_create, observer_update


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

CREATE_TEMPLATE = "observer_create.sh.j2"

# ----------------
# Global variables
# ----------------

log = logging.getLogger(__name__.split(".")[-1])
package = ".".join(__name__.split(".")[:-2])

host = decouple.config("TESSDB_ADMIN_HOST", default="localhost")
port = decouple.config("TESSDB_ADMIN_PORT", cast=int, default=8080)

render = functools.partial(render_from, package)

# ================
# MAIN ENTRY POINT
# ================


def cli_observer_create(args: Namespace) -> None:
    candidate = ObserverInfo(
        type=args.type,
        name=args.name,
        affiliation=args.affiliation,
        acronym=args.acronym,
        website_url=args.website_url,
        email=args.email,
    )
    with TessDbServer(host=host, port=port, test=args.test):
        with Session() as session:
            with session.begin():
                log.info("Registering observer: %s", dict(candidate))
                observer_create(
                    session,
                    candidate,
                    args.dry_run,
                )


def cli_observer_update(args: Namespace) -> None:
    candidate = ObserverInfo(
        type=args.type,
        name=args.name,
        affiliation=args.affiliation,
        acronym=args.acronym,
        website_url=args.website_url,
        email=args.email,
    )
    with TessDbServer(host=host, port=port, test=args.test):
        with Session() as session:
            with session.begin():
                log.info("Updating observer: %s", dict(candidate))
                observer_update(
                    session,
                    candidate,
                    args.fix,
                    args.dry_run,
                )

def cli_observer_generate(args: Namespace) -> None:
    with open(args.input_csv, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        observers = [dict(row) for row in reader]
    try:
        observers = list(filter(lambda x: ObserverType(x["type"].title()) is not None, observers))
    except Exception:
        log.error("Observer Type is not valid")
    else:
        log.info("found %d records", len(observers))
        obs_by_name = defaultdict(list)
        for obs in observers:
            obs_by_name[obs["name"]].append(obs)
        observers = [val[0] for key, val in obs_by_name.items()]
        log.info("reduced to %d observers", len(observers))
        context = {"observers": observers}
        script = render(CREATE_TEMPLATE, context)
        with open(args.output_script, "w") as outfile:
            outfile.write(script)
        log.info("script '%s' generated", args.output_script)


def add_args(parser: ArgumentParser) -> None:
    subparser = parser.add_subparsers(dest="command", required=True)
    p = subparser.add_parser(
        "create",
        parents=[prs.observer(), prs.dry(), prs.test()],
        help="Create new observer",
    )
    p.set_defaults(func=cli_observer_create)
    p = subparser.add_parser(
        "update",
        parents=[prs.observer(), prs.dry(), prs.fix(), prs.test()],
        help="Update existing observer",
    )
    p.set_defaults(func=cli_observer_update)
    p = subparser.add_parser(
        "generate",
        parents=[
            prs.ifile(),
            prs.ofile(),
            prs.dry(),
        ],
        help="Generate observers creation script from observers CSV",
    )
    p.set_defaults(func=cli_observer_generate)


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

# ----------------------------------------------------------------------
# Copyright (c) 2024 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------

# --------------------
# System wide imports
# -------------------

from argparse import ArgumentParser

# ---------------------------
# Third-party library imports
# ----------------------------

from lica.validators import vfile, vdate
from tessdbdao import ObserverType, PhotometerModel


def test() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-te",
        "--test",
        default=False,
        action="store_true",
        help="Test Mode, do not pause tessdb-server",
    )
    return parser


def readings() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-re",
        "--readings",
        default=False,
        action="store_true",
        help="Update location and observer in readings too",
    )
    parser.add_argument(
        "-si",
        "--since",
        type=vdate,
        default=None,
        metavar="<YYYY-MM-DD>",
        help="update readings since (defaults to %(default)s)",
    )
    parser.add_argument(
        "-un",
        "--until",
        type=vdate,
        default=None,
        metavar="<YYYY-MM-DD>",
        help="update readings until (defaults to %(default)s)",
    )
    return parser


def name() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-na",
        "--name",
        type=str,
        required=True,
        help="Photometer name",
    )
    return parser


def every() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-ev",
        "--every",
        type=int,
        default=1,
        help="Chooses 1 every N reading to insert into the database",
    )
    return parser


def batch() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-bs",
        "--batch-size",
        type=int,
        default=1440,  # One day of readings @ 1 reading/min
        help="Batch size when uploading to database",
    )
    return parser


def ifile() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-ic",
        "--input-csv",
        type=vfile,
        required=True,
        help="Input CSV file",
    )
    return parser


def ofile() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-os",
        "--output-script",
        type=str,
        required=True,
        help="Output shell script",
    )
    return parser


def dry() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-dr",
        "--dry-run",
        default=False,
        action="store_true",
        help="Dry run, do not update database",
    )
    return parser


def observer() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-ty",
        "--type",
        type=ObserverType,
        default=None,
        help="Observer Type (person, organization)",
    )
    parser.add_argument(
        "-ob",
        "--observer",
        type=str,
        default=None,
        help="Observer name",
    )
    return parser


def location() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-pl",
        "--place",
        type=str,
        default=None,
        help="Place name",
    )
    return parser


def tstamp() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-ts",
        "--timestamp",
        type=vdate,
        default=None,
        metavar="<YYYY-MM-DDTHH:MM:SS>",
        help="Registration UTC timestamp (defaults to %(default)s = current UTC time)",
    )
    return parser


def photom() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-ma",
        "--mac-address",
        type=str,
        required=True,
        help="Photometer MAC address",
    )
    parser.add_argument(
        "-na",
        "--name",
        type=str,
        required=True,
        help="Photometer name",
    )
    parser.add_argument(
        "-mo",
        "--model",
        type=PhotometerModel,
        default=PhotometerModel.TESSW,
        help="Photometer model",
    )
    parser.add_argument(
        "-fi",
        "--firmware",
        type=str,
        required=True,
        help="Photometer name",
    )
    parser.add_argument(
        "-au",
        "--authorise",
        default=False,
        action="store_true",
        help="Authorise to store readings",
    )
    parser.add_argument(
        "--zp1",
        type=float,
        required=True,
        help="Zero Point 1 [mag/arcsec^2]",
    )
    parser.add_argument(
        "-o1",
        "--offset1",
        type=float,
        default=0.0,
        help="Frequency offset 1 [Hz] (defaults to %(default)s)",
    )
    parser.add_argument(
        "-f1",
        "--filter1",
        type=str,
        default="UV/IR-740",
        help="Filter 1 (defaults to %(default)s)",
    )

    parser.add_argument(
        "--zp2",
        type=float,
        default=None,
        help="Zero Point 2 [mag/arcsec^2] (defaults to %(default)s)",
    )
    parser.add_argument(
        "-o2",
        "--offset2",
        type=float,
        default=None,
        help="Frequency offset 2 [Hz] (defaults to %(default)s)",
    )
    parser.add_argument(
        "-f2",
        "--filter2",
        type=str,
        default=None,
        help="Filter 2 (defaults to %(default)s)",
    )

    parser.add_argument(
        "--zp3",
        type=float,
        default=None,
        help="Zero Point 3 [mag/arcsec^2] (defaults to %(default)s)",
    )
    parser.add_argument(
        "-o3",
        "--offset3",
        type=float,
        default=None,
        help="Frequency offset 3 [Hz] (defaults to %(default)s)",
    )
    parser.add_argument(
        "-f3",
        "--filter3",
        type=str,
        default=None,
        help="Filter 3 (defaults to %(default)s)",
    )

    parser.add_argument(
        "--zp4",
        type=float,
        default=None,
        help="Zero Point 4 [mag/arcsec^2] (defaults to %(default)s)",
    )
    parser.add_argument(
        "-o4",
        "--offset4",
        type=float,
        default=None,
        help="Frequency offset 4 [Hz] (defaults to %(default)s)",
    )
    parser.add_argument(
        "-f4",
        "--filter4",
        type=str,
        default=None,
        help="Filter 4 (defaults to %(default)s)",
    )

    return parser

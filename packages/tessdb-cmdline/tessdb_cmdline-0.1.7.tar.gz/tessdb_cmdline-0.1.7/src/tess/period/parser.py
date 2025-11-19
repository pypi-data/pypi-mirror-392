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


def phot() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-na",
        "--name",
        type=str,
        required=True,
        help="photometer name",
    )
    parser.add_argument(
        "-ns",
        "--num-samples",
        type=int,
        default=None,
        help="Number of samples (defaults to %(default)s = indefinite",
    )
    return parser

# ----------------------------------------------------------------------
# Copyright (c) 2024 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------

# --------------------
# System wide imports
# -------------------

import os
import re
import glob
import logging
import datetime  # necessary for eval
from itertools import batched
from collections import defaultdict
import functools

from typing import Optional, List, Dict, Mapping, Tuple, Any

# -------------------
# Third party imports
# -------------------

from sqlalchemy import select, func

from tessdbdao import TimestampSource
from tessdbdao.noasync import NameMapping
from zptessdao.noasync import SummaryView


# --------------
# local imports
# -------------

from .dao import TdbSession, ZptSession

# ----------------
# Global variables
# ----------------

package = ".".join(__name__.split(".")[:-1])
log = logging.getLogger(__name__.split(".")[-1])

TSTAMP_PATTERN = re.compile("(.+)'tstamp_src': <TimestampSource.+: '(.+)'>(.+)")


def is_tess4c(readings: Mapping[str, Any]) -> bool:
    return "freq4" in readings


def windowed3(start: Optional[int], end: Optional[int], path: str) -> bool:
    path = os.path.basename(path)
    if start is not None and path < f"tessdb.log-{start}":
        return False
    if end is not None and path > f"tessdb.log-{end}":
        return False
    return True


def filtered_log_files(log_dir: str, start: Optional[int], end: Optional[int]) -> List[str]:
    template = os.path.join(log_dir, "tessdb.log-????????")
    files = glob.iglob(template)
    windowed = functools.partial(windowed3, start, end)
    return sorted(filter(windowed, files), reverse=True)


def context(registration_needed: bool, readings: List[Dict[str, Any]]) -> Dict[str, Any]:
    ctx = dict()
    ctx["registration_needed"] = registration_needed
    ctx["model"] = "TESS4C" if is_tess4c(readings[0]) else "TESS-W"
    ctx["readings"] = list(enumerate(batched(readings, 10000), start=1))
    return ctx


def fix_tstamp_src_enum(value: str) -> str:
    matchobj = TSTAMP_PATTERN.search(value)
    groups = matchobj.groups()
    value = groups[0] + f"'tstamp_src': '{groups[1]}'" + groups[2]
    return value


# The new format in tessdb-server-ng
def fix_old_format(reading: dict[str, Any]) -> dict[str, Any]:
    del reading["rev"]
    reading["sequence_number"] = reading["seq"]
    del reading["seq"]
    reading["signal_strength"] = reading["wdBm"]
    del reading["wdBm"]
    reading["sky_temperature"] = reading["tsky"]
    del reading["tsky"]
    reading["box_temperature"] = reading["tamb"]
    del reading["tamb"]
    reading["longitude"] = None
    reading["latitude"] = None
    reading["elevation"] = None
    reading["altitude"] = None
    reading["azimuth"] = None
    return reading


def collect_readings_for(
    name: str, log_dir: str, start: int, end: int, batch_size: int
) -> List[Dict[str, Any]]:
    # This pattern captures both old and new log format when tessdb-server-ng was placed in production
    pattern = rf".{{42,60}} No TESS {name} registered ! => (.+)"
    pattern = re.compile(pattern)
    files = filtered_log_files(log_dir, start, end)
    readings = list()
    for i, batch in enumerate(batched(files, batch_size), start=1):
        batched_readings = list()
        batched_lengths = list()
        N = len(batch)
        for j, path in enumerate(batch, start=1):
            with open(path, "r") as fd:
                file_readings = list()
                for line in fd.readlines():
                    matchobj = pattern.search(line)
                    if matchobj:
                        found = matchobj.groups()[0]
                        try:
                            reading = eval(found)
                        except SyntaxError:
                            found = fix_tstamp_src_enum(found)
                            reading = eval(found)
                        if "valid_current" in reading:
                            del reading["valid_current"]
                        if "seq" in reading:
                            reading = fix_old_format(reading)
                        reading["tstamp"] = reading["tstamp"].replace(microsecond=0)
                        file_readings.append(reading)
                batched_readings.extend(file_readings)
                batched_lengths.append(len(batched_readings))
                log.info(
                    "[%s] Analyzing batch #%d (%02d/%02d), %s for readings, %d found",
                    name,
                    i,
                    j,
                    N,
                    path,
                    len(file_readings),
                )
        readings.extend(batched_readings)
        if all([batched_lengths[0] == n for n in batched_lengths]):
            log.warn("Stopping analysis in batch #%d . No activity was found.", i)
            break
    log.info("Sorting %s readings by timestamp", name)
    return sorted(readings, key=lambda x: x["tstamp"])


def already_registered(name: str) -> bool:
    with TdbSession() as session:
        query = select(func.count("*")).select_from(NameMapping).where(NameMapping.name == name)
        N = session.scalars(query).one()
        log.info("Found %d entries for %s", N, name)
        if N > 0:
            query = select(NameMapping).where(NameMapping.name == name)
            result_set = session.scalars(query)
            for result in result_set:
                log.info(result)
    return N > 0


def find_photometer_details(name: str) -> Tuple[str, float]:
    with ZptSession() as session:
        query = select(SummaryView.mac, SummaryView.zero_point, SummaryView.firmware).where(
            SummaryView.name == name
        )
        result_set = session.execute(query)
    return result_set


def to_date(value: str) -> str:
    return datetime.datetime.strptime(value, "%Y%m%d").strftime("%Y-%m-%dT%H:%M:%S")


def collect_references(
    log_dir: str, start: int, end: int
) -> List[Tuple[str, str, int, str, str, bool, Any]]:
    pattern = r".{42,60} No TESS (stars\d{1,8}) registered ! => "
    pattern = re.compile(pattern)
    names = set()
    counts = dict()
    files_per_name = defaultdict(set)
    files = filtered_log_files(log_dir, start, end)
    for path in files:
        with open(path, "r") as fd:
            log.info("Analyzing %s, %d photometers found so far", path, len(names))
            for line in reversed(fd.readlines()):
                matchobj = pattern.search(line)
                if matchobj:
                    name = matchobj.groups()[0]
                    names.add(name)
                    counts[name] = counts.get(name, 0) + 1
                    files_per_name[name].add(os.path.basename(path))

    summary_info = [
        (
            name,
            f"{counts[name]:8d}",
            sorted(files_per_name[name])[0].split("-")[-1][:-2],
            sorted(files_per_name[name])[0],
            sorted(files_per_name[name])[-1],
            already_registered(name),
            tuple(find_photometer_details(name)),
        )
        for name in names
    ]
    summary_info = sorted(summary_info, reverse=True, key=lambda x: x[4])
    # log.info(summary_info)
    # "tstamp", "name", "mac", "model", "firmware", "zp1", "zp2", "zp3", "zp4", "place", "obs_type", "obs_name")
    registry_info = [
        (
            to_date(item[3][11:]),
            item[0],
            item[-1][0][0],
            "TESS-W",
            item[-1][0][2],
            item[-1][0][1],
            None,
            None,
            None,
            None,
            None,
        )
        for item in summary_info
        if len(item[-1]) == 1
    ]
    return summary_info, registry_info

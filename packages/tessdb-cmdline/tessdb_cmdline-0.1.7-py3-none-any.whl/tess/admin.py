# ----------------------------------------------------------------------
# Copyright (c) 2024 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------

# --------------------
# System wide imports
# -------------------

import logging
import time
from datetime import datetime, timedelta

# -------------------
# Third party imports
# -------------------

import requests

# ----------------
# Global variables
# ----------------

log = logging.getLogger(__name__.split(".")[-2])


class TooCloseError(RuntimeError):
    """Time too close to tessdb database backup"""
    def __str__(self):
        s = self.__doc__
        if self.args:
            s = '{0}: {1}'.format(s, self.args[0])
        s = '{0}.'.format(s)
        return s

# Contexct manager tp coordinate access to the underlying database
# with TessDB server, making it to stop
# We do not cacth any exception, since we are not handling them and we need to abort anyway
# The timestamp constructor is only needed for testing purposes


class TessDbServer:
    BEFORE = timedelta(hours=1)
    AFTER = timedelta(minutes=30)
    SLEEP = 3

    def __init__(
        self, host: str, port: int, timeout=1, test: bool = False, timestamp: datetime = None
    ):
        self._host = host
        self._port = port
        self._pause_url = f"http://{host}:{port}/v1/server/pause"
        self._resume_url = f"http://{host}:{port}/v1/server/resume"
        self._timeout = timeout
        self._test = test
        self._tstamp = timestamp

    def _assert_timestamp(self) -> None:
        self._tstamp = datetime.now() if self._tstamp is None else self._tstamp
        noon = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
        if noon - TessDbServer.BEFORE <= self._tstamp <= noon + TessDbServer.AFTER:
            raise TooCloseError(self._tstamp.strftime("%Y-%m-%d %H:%M:%S"))

    def __enter__(self) -> None:
        if not self._test:
            self._assert_timestamp()
            log.info("requesting a pause to tessdb server on %s,%d", self._host, self._port)
            r = requests.post(self._pause_url, data={}, timeout=self._timeout)
            r.raise_for_status()
            response = r.json()
            log.info(response)
            time.sleep(TessDbServer.SLEEP)


    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type is None and not self._test:
            log.info("requesting tessdb server on %s:%d to resume", self._host, self._port)
            r = requests.post(self._resume_url, data={}, timeout=self._timeout)
            r.raise_for_status()
            response = r.json()
            log.info(response)
        elif exc_type is not None:
            log.error(
                "an exception has been registered withn the %s context manager",
                self.__class__.__name__,
            )
        return False

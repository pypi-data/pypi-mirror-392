# ----------------------------------------------------------------------
# Copyright (c) 2024 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------

# --------------------
# System wide imports
# -------------------

import json
import asyncio
from datetime import datetime
import logging
import statistics
from itertools import pairwise
from typing import Any, Optional, Dict, AsyncIterator, TypeVar, List, Tuple

# ---------------------------
# Third-party library imports
# ----------------------------

import decouple
import aiomqtt
from aiomqtt.client import ProtocolVersion

# --------------
# local imports
# -------------


# ---------
# CONSTANTS
# ---------


# ------------------
# Additional Classes
# ------------------

# ----------------
# Global variables
# ----------------

log = logging.getLogger(__name__.split(".")[-2])
proto_log = logging.getLogger("MQTT")

T = TypeVar("T")

# -----------------
# Auxiliar functions
# ------------------


async def aioenumerate(aiter: AsyncIterator[T], start: int = 0) -> AsyncIterator[Tuple[int, T]]:
    idx = start
    async for item in aiter:
        yield idx, item
        idx += 1


# --------------
# The MQTT task
# --------------


def average_stdev(samples: List[Dict[str, Any]]) -> Tuple[float, float]:
    deltas = [
        (s2["T"] - s1["T"]).total_seconds() / (s2["seq"] - s1["seq"])
        for (s1, s2) in pairwise(samples)
    ]
    return statistics.mean(deltas), statistics.stdev(deltas)


async def subscriber(phot_name: str, limit: Optional[int]) -> None:
    interval = 5
    log.info("Starting MQTT subscriber")
    client = aiomqtt.Client(
        decouple.config("MQTT_HOST"),
        decouple.config("MQTT_PORT", cast=int),
        username=decouple.config("MQTT_USERNAME"),
        password=decouple.config("MQTT_PASSWORD"),
        identifier=decouple.config("MQTT_CLIENT_ID"),
        transport=decouple.config("MQTT_TRANSPORT"),
        logger=proto_log,
        keepalive=60,
        protocol=ProtocolVersion.V311,
    )
    topic = f"STARS4ALL/{phot_name}/reading"
    try:
        async with client:
            log.info("Subscribing to %s", topic)
            await client.subscribe(topic, qos=2)
            samples = list()
            async for i, message in aioenumerate(client.messages, start=1):
                tstamp = datetime.now()
                row = json.loads(message.payload.decode("utf-8"))
                if message.retain:
                    log.info("[%s] Discarding retained sample #%d", phot_name, row["seq"])
                    continue
                row["T"] = tstamp
                samples.append(row)
                log.info("[%s] Got sample #%d", phot_name, row["seq"])
                if len(samples) > 2:
                    mean, stdev = average_stdev(samples)
                    log.info(
                        "[%s] Tx: \u03bc = %.02f sec., \u03c3 = %.03f sec. over %d samples",
                        phot_name,
                        mean,
                        stdev,
                        len(samples),
                    )
                if limit is not None and i == limit:
                    break
    except json.JSONDecodeError:
        log.error("Invalid JSON in payload=%s", payload)
    except aiomqtt.MqttError:
        log.info(f"Connection lost; Reconnecting in {interval} seconds ...")
        await asyncio.sleep(interval)

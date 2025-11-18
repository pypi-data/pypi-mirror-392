import pytest
import logging
import requests
from datetime import datetime
from tess.admin import TessDbServer, TooCloseError

bad_t = datetime.now().replace(hour=11, minute=49, second=0)
good_t = datetime.now().replace(hour=12, minute=31, second=0)

log = logging.getLogger(__name__.split(".")[-1])


# Different window sizes
fail_conn_data = (("localhost",8081),("calyx.hst.ucm.es",8080))
ok_conn_data = (("localhost",8080),)


@pytest.fixture(params=fail_conn_data)
def fail_server(request) -> TessDbServer:
    return TessDbServer(host=request.param[0], port=request.param[1], timestamp=good_t)

@pytest.fixture(params=ok_conn_data)
def ok_server(request) -> TessDbServer:
    return TessDbServer(host=request.param[0], port=request.param[1], timestamp=good_t)

@pytest.fixture(params=fail_conn_data)
def noop_server(request) -> TessDbServer:
    return TessDbServer(host=request.param[0], port=request.param[1], test=True)

@pytest.fixture(params=ok_conn_data)
def fail_time(request) -> TessDbServer:
    return TessDbServer(host=request.param[0], port=request.param[1], timestamp=bad_t)


def test_enter_1(fail_server):
    with pytest.raises(Exception) as exc_info: 
        fail_server.__enter__()
    assert exc_info.type in (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout)
    log.info(exc_info.type)

def test_enter_2(fail_time):
    with pytest.raises(Exception) as exc_info: 
        fail_time.__enter__()
    assert exc_info.type is TooCloseError
    log.info(exc_info.type)

def test_enter_3(noop_server):
    noop_server.__enter__()
    

def test_exit_1(fail_server):
    with pytest.raises(Exception) as exc_info: 
        fail_server.__exit__(None, None, None)
    log.info(exc_info.type)
    assert exc_info.type in (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout)

def test_exit_3(noop_server):
    noop_server.__exit__(None, None, None)


def test_fail_with_1(fail_server):
    with pytest.raises(Exception) as exc_info:
        with fail_server:
            log.info("should never print this")
    log.info(exc_info.type)
    assert exc_info.type in (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout)

def test_fail_with_2(fail_time):
    with pytest.raises(Exception) as exc_info:
        with fail_time:
            log.info("should never print this")
    log.info(exc_info.type)
    assert exc_info.type is TooCloseError

def test_ok_with(ok_server):
    with ok_server:
        log.info("Doing DB stuff")

def test_noop_with(noop_server):
    with noop_server:
        log.info("Doing DB stuff")
# -*- coding: utf-8 -*-
try:
    from types import SimpleNamespace
except ImportError:
    class SimpleNamespace(object):
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

import pytest
from django.http import HttpResponse
from django.test import RequestFactory
from nati_log.middleware import NatiLogMiddleware


class DummyClient(object):
    def __init__(self):
        self.calls = []

    def debug(self, mensaje, datos=None, fecha=None):
        self.calls.append(("debug", mensaje, datos))

    def info(self, mensaje, datos=None, fecha=None):
        self.calls.append(("info", mensaje, datos))

    def warning(self, mensaje, datos=None, fecha=None):
        self.calls.append(("warning", mensaje, datos))

    def error(self, mensaje, datos=None, fecha=None):
        self.calls.append(("error", mensaje, datos))

    def critical(self, mensaje, datos=None, fecha=None):
        self.calls.append(("critical", mensaje, datos))


@pytest.fixture
def rf():
    return RequestFactory()


def make_response(status=200):
    resp = HttpResponse("ok")
    resp.status_code = status
    return resp


def test_middleware_registra_info_por_defecto(settings, monkeypatch, rf):
    settings.NATILOG = {
        "API_URL": "http://fake/api",
        "API_URL_LOGIN": "http://fake/api/auth/",
        "APP_ID": 1,
        "USERNAME": "user",
        "PASSWORD": "pass",
        "EVENT_LEVELS": {
            "DEBUG": True,
            "INFO": True,
            "WARNING": True,
            "ERROR": True,
            "CRITICAL": True,
        },
    }
    dummy = DummyClient()
    monkeypatch.setattr("nati_log.middleware.NatiLogClient", lambda **_: dummy)

    middleware = NatiLogMiddleware(lambda req: make_response(200))
    request = rf.get("/path")
    request.user = SimpleNamespace(username="tester")

    middleware(request)

    assert ("debug", "Request recibido: GET /path", {"usuario": "tester"}) in dummy.calls
    assert any(call[0] == "info" for call in dummy.calls)


def test_middleware_filtra_niveles(settings, monkeypatch, rf):
    settings.NATILOG = {
        "API_URL": "http://fake/api",
        "API_URL_LOGIN": "http://fake/api/auth/",
        "APP_ID": 1,
        "USERNAME": "user",
        "PASSWORD": "pass",
        "EVENT_LEVELS": {
            "DEBUG": False,
            "INFO": False,
            "WARNING": True,
            "ERROR": True,
            "CRITICAL": True,
        },
    }
    dummy = DummyClient()
    monkeypatch.setattr("nati_log.middleware.NatiLogClient", lambda **_: dummy)

    middleware = NatiLogMiddleware(lambda req: make_response(302))
    request = rf.get("/redirect")

    middleware(request)

    tipos = set(call[0] for call in dummy.calls)
    assert "debug" not in tipos
    assert "info" not in tipos
    assert "warning" in tipos


def test_middleware_registra_error(settings, monkeypatch, rf):
    settings.NATILOG = {
        "API_URL": "http://fake/api",
        "API_URL_LOGIN": "http://fake/api/auth/",
        "APP_ID": 1,
        "USERNAME": "user",
        "PASSWORD": "pass",
        "EVENT_LEVELS": {
            "DEBUG": True,
            "INFO": True,
            "WARNING": True,
            "ERROR": True,
            "CRITICAL": True,
        },
    }
    dummy = DummyClient()
    monkeypatch.setattr("nati_log.middleware.NatiLogClient", lambda **_: dummy)

    middleware = NatiLogMiddleware(lambda req: make_response(404))
    request = rf.get("/not-found")
    request.user = SimpleNamespace(username="tester")

    middleware(request)

    assert any(call[0] == "error" for call in dummy.calls)


def test_middleware_sin_cliente_retorna(settings, monkeypatch, rf):
    settings.NATILOG = {
        "API_URL": "http://fake/api",
        "API_URL_LOGIN": "http://fake/api/auth/",
        "APP_ID": 1,
        "USERNAME": "user",
        "PASSWORD": "pass",
        "EVENT_LEVELS": {"DEBUG": True, "INFO": True, "WARNING": True, "ERROR": True, "CRITICAL": True},
    }
    monkeypatch.setattr("nati_log.middleware.NatiLogClient", lambda **_: None)

    middleware = NatiLogMiddleware(lambda req: make_response(200))
    request = rf.get("/noop")
    middleware(request)


def test_middleware_registra_critical(settings, monkeypatch, rf):
    settings.NATILOG = {
        "API_URL": "http://fake/api",
        "API_URL_LOGIN": "http://fake/api/auth/",
        "APP_ID": 1,
        "USERNAME": "user",
        "PASSWORD": "pass",
        "EVENT_LEVELS": {"DEBUG": True, "INFO": True, "WARNING": True, "ERROR": True, "CRITICAL": True},
    }
    dummy = DummyClient()
    monkeypatch.setattr("nati_log.middleware.NatiLogClient", lambda **_: dummy)

    middleware = NatiLogMiddleware(lambda req: make_response(503))
    request = rf.get("/boom")
    request.user = SimpleNamespace(username="tester")

    middleware(request)

    assert any(call[0] == "critical" for call in dummy.calls)


def test_middleware_registra_warning(settings, monkeypatch, rf):
    settings.NATILOG = {
        "API_URL": "http://fake/api",
        "API_URL_LOGIN": "http://fake/api/auth/",
        "APP_ID": 1,
        "USERNAME": "user",
        "PASSWORD": "pass",
        "EVENT_LEVELS": {
            "DEBUG": True,
            "INFO": True,
            "WARNING": True,
            "ERROR": True,
            "CRITICAL": True,
        },
    }
    dummy = DummyClient()
    monkeypatch.setattr("nati_log.middleware.NatiLogClient", lambda **_: dummy)

    middleware = NatiLogMiddleware(lambda req: make_response(302))
    request = rf.get("/redirect")
    request.user = SimpleNamespace(username="tester")

    middleware(request)

    assert any(call[0] == "warning" for call in dummy.calls)
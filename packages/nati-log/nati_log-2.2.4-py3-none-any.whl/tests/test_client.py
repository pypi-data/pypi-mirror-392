# -*- coding: utf-8 -*-
import datetime
import pytest
import requests
from nati_log.client import NatiLogClient


@pytest.fixture
def api_urls():
    return {
        "api": "http://fake-api/api",
        "login": "http://fake-api/api/auth/usuarios/login/",
        "app": "http://fake-api/api/aplicaciones/5",
        "evento": "http://fake-api/api/evento/",
    }


def _build_client(requests_mock, api_urls, app_estado=True, token="token-1"):
    requests_mock.post(
        api_urls["login"],
        json={"access": token},
        status_code=200,
    )
    requests_mock.get(
        api_urls["app"],
        json={"estado": app_estado},
        status_code=200,
    )
    return NatiLogClient(
        api_url=api_urls["api"],
        api_url_login=api_urls["login"],
        app_id=5,
        username="user",
        password="pass",
    )


def test_registrar_evento_success(requests_mock, api_urls):
    client = _build_client(requests_mock, api_urls)
    requests_mock.post(
        api_urls["evento"],
        json={"status": "ok"},
        status_code=201,
    )

    resp = client.info("Evento exitoso", datos={"key": "value"})
    assert resp == {"status": "ok"}

    last = requests_mock.last_request
    assert last.headers["Authorization"] == "Bearer token-1"
    assert last.json()["tipo_evento"] == "INFO"
    assert last.json()["datos"]["key"] == "value"


def test_registrar_evento_app_inactiva_omite_envio(requests_mock, api_urls):
    client = _build_client(requests_mock, api_urls, app_estado=False)

    result = client.info("No debe enviarse")
    assert result == {"detail": "Aplicación inactiva. Evento omitido."}
    assert len(requests_mock.request_history) == 2  # login + estado, sin POST de evento


def test_registrar_evento_reintenta_en_401(requests_mock, api_urls):
    requests_mock.post(
        api_urls["login"],
        [
            {"json": {"access": "token-1"}, "status_code": 200},
            {"json": {"access": "token-2"}, "status_code": 200},
        ],
    )
    requests_mock.get(api_urls["app"], json={"estado": True}, status_code=200)
    requests_mock.post(
        api_urls["evento"],
        [
            {"status_code": 401},
            {"json": {"status": "ok"}, "status_code": 201},
        ],
    )

    client = NatiLogClient(
        api_url=api_urls["api"],
        api_url_login=api_urls["login"],
        app_id=5,
        username="user",
        password="pass",
    )
    resp = client.error("Debe reintentar")
    assert resp == {"status": "ok"}

    evento_calls = [req for req in requests_mock.request_history if req.url == api_urls["evento"]]
    assert len(evento_calls) == 2
    assert evento_calls[-1].headers["Authorization"] == "Bearer token-2"


def test_registrar_evento_sin_token_levanta_http_error(requests_mock, api_urls):
    requests_mock.post(api_urls["login"], status_code=401)
    client = NatiLogClient(
        api_url=api_urls["api"],
        api_url_login=api_urls["login"],
        app_id=5,
        username="user",
        password="pass",
    )

    requests_mock.post(api_urls["evento"], status_code=401)
    with pytest.raises(requests.exceptions.HTTPError):
        client.warning("Debe fallar")


def test_registrar_evento_con_fecha_personalizada(requests_mock, api_urls):
    client = _build_client(requests_mock, api_urls)
    requests_mock.post(
        api_urls["evento"],
        json={"status": "ok"},
        status_code=201,
    )

    fecha = datetime.datetime(2024, 1, 1, 12, 0, 0).isoformat()
    client.debug("Con fecha", fecha=fecha)

    last = requests_mock.last_request
    assert last.json()["fecha"] == fecha
    assert last.json()["tipo_evento"] == "DEBUG"


def test_get_token_exception_deja_token_none(requests_mock, api_urls):
    requests_mock.post(
        api_urls["login"],
        exc=requests.exceptions.ConnectTimeout,
    )

    client = NatiLogClient(
        api_url=api_urls["api"],
        api_url_login=api_urls["login"],
        app_id=5,
        username="user",
        password="pass",
    )
    assert client.token is None
    assert client.app_activa is True


def test_registrar_evento_retry_sin_token_levanta_error(requests_mock, api_urls):
    requests_mock.post(
        api_urls["login"],
        [
            {"json": {"access": "token-1"}, "status_code": 200},
            {"status_code": 500},
        ],
    )
    requests_mock.get(api_urls["app"], json={"estado": True}, status_code=200)
    requests_mock.post(api_urls["evento"], status_code=401)

    client = NatiLogClient(
        api_url=api_urls["api"],
        api_url_login=api_urls["login"],
        app_id=5,
        username="user",
        password="pass",
    )

    with pytest.raises(requests.exceptions.HTTPError):
        client.warning("Debe fallar tras reintento sin token")


def test_registrar_evento_critical(requests_mock, api_urls):
    client = _build_client(requests_mock, api_urls)
    requests_mock.post(
        api_urls["evento"],
        json={"status": "ok"},
        status_code=201,
    )

    client.critical("Falla crítica")

    last = requests_mock.last_request
    assert last.json()["tipo_evento"] == "CRITICAL"


def test_actualizar_estado_aplicacion_refresca_token(requests_mock, api_urls):
    requests_mock.post(
        api_urls["login"],
        [
            {"json": {"access": "token-1"}, "status_code": 200},
            {"json": {"access": "token-2"}, "status_code": 200},
        ],
    )
    requests_mock.get(
        api_urls["app"],
        [
            {"status_code": 401},
            {"json": {"estado": False}, "status_code": 200},
        ],
    )

    client = NatiLogClient(
        api_url=api_urls["api"],
        api_url_login=api_urls["login"],
        app_id=5,
        username="user",
        password="pass",
    )

    assert client.token == "token-2"
    assert client.app_activa is False


def test_actualizar_estado_aplicacion_error_mantiene_activa(requests_mock, api_urls):
    requests_mock.post(api_urls["login"], json={"access": "token"}, status_code=200)
    requests_mock.get(api_urls["app"], exc=requests.exceptions.ReadTimeout)

    client = NatiLogClient(
        api_url=api_urls["api"],
        api_url_login=api_urls["login"],
        app_id=5,
        username="user",
        password="pass",
    )

    assert client.app_activa is True
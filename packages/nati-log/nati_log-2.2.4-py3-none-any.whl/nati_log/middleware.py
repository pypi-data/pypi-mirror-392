from django.conf import settings
from .client import NatiLogClient


class NatiLogMiddleware:
    def __init__(self, get_response):
        """
        Middleware para registrar eventos automáticamente en NatiLog.
        Args:
        :param get_response: callable - La función para obtener la respuesta de la vista
        """

        self.get_response = get_response
        config = getattr(settings, "NATILOG", {})
        self.levels = config.get(
            "EVENT_LEVELS",
            {"DEBUG": True, "INFO": True, "WARNING": True, "ERROR": True, "CRITICAL": True},
        )
        self.natilog = NatiLogClient(
            api_url=config.get("API_URL"),
            api_url_login=config.get("API_URL_LOGIN"),
            app_id=config.get("APP_ID"),
            username=config.get("USERNAME"),
            password=config.get("PASSWORD"),
        )

    def __call__(self, request):
        """
        Procesa la solicitud y registra eventos en NatiLog.
        Args:
        :param request: HttpRequest - La solicitud entrante
        :returns: HttpResponse - La respuesta generada por la vista
        """
        response = self.get_response(request)

        if not self.natilog:
            return response

        try:
            if self.levels.get("DEBUG", True):
                self.natilog.debug(
                    f"Request recibido: {request.method} {request.path}",
                    datos={"usuario": getattr(request.user, "username", None)},
                )

            if 200 <= response.status_code < 300 and self.levels.get("INFO", True):
                self.natilog.info(
                    f"Request OK: {request.method} {request.path}",
                    datos={"status_code": response.status_code},
                )
            elif 300 <= response.status_code < 400 and self.levels.get("WARNING", True):
                self.natilog.warning(
                    f"Redirect: {request.method} {request.path}",
                    datos={"status_code": response.status_code},
                )
            elif 400 <= response.status_code < 500 and self.levels.get("ERROR", True):
                self.natilog.error(
                    f"Client Error {response.status_code}: {request.method} {request.path}",
                    datos={"status_code": response.status_code},
                )
            elif response.status_code >= 500 and self.levels.get("CRITICAL", True):
                self.natilog.critical(
                    f"Server Error {response.status_code}: {request.method} {request.path}",
                    datos={"status_code": response.status_code},
                )
        except Exception as exc:
            print(f"Error al registrar evento en NatiLog: {exc}")

        return response

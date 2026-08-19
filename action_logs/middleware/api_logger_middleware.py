import json
import logging
import time

from django.conf import settings
from django.urls import resolve
from django.utils import timezone

from action_logs.start_logger_when_server_starts import LOGGER_THREAD
from action_logs import API_LOGGER_SIGNAL
from action_logs.utils import get_headers, get_client_ip, mask_sensitive_data


class APILoggerMiddleware:
    """
    Production-ready DRF API Logger Middleware
    Works with async queue + bulk DB insert
    """

    def __init__(self, get_response):
        self.get_response = get_response

        self.DRF_API_LOGGER_DATABASE = getattr(settings, "DRF_API_LOGGER_DATABASE", False)
        self.DRF_API_LOGGER_SIGNAL = getattr(settings, "DRF_API_LOGGER_SIGNAL", False)

        self.DRF_API_LOGGER_SKIP_URL_NAME = getattr(settings, "DRF_API_LOGGER_SKIP_URL_NAME", [])
        self.DRF_API_LOGGER_SKIP_NAMESPACE = getattr(settings, "DRF_API_LOGGER_SKIP_NAMESPACE", [])
        self.DRF_API_LOGGER_METHODS = getattr(settings, "DRF_API_LOGGER_METHODS", [])
        self.DRF_API_LOGGER_STATUS_CODES = getattr(settings, "DRF_API_LOGGER_STATUS_CODES", [])

    def __call__(self, request):

        if not (self.DRF_API_LOGGER_DATABASE or self.DRF_API_LOGGER_SIGNAL):
            return self.get_response(request)

        try:
            resolver = resolve(request.path_info)
            url_name = resolver.url_name
            namespace = resolver.namespace
        except Exception:
            url_name = None
            namespace = None

        if namespace == "admin":
            return self.get_response(request)

        if url_name and url_name in self.DRF_API_LOGGER_SKIP_URL_NAME:
            return self.get_response(request)

        if namespace and namespace in self.DRF_API_LOGGER_SKIP_NAMESPACE:
            return self.get_response(request)

        start_time = time.time()

        request_data = {}
        try:
            if request.body:
                request_data = json.loads(request.body)
        except Exception:
            request_data = {}

        response = self.get_response(request)

        if self.DRF_API_LOGGER_STATUS_CODES and response.status_code not in self.DRF_API_LOGGER_STATUS_CODES:
            return response

        method = request.method
        if self.DRF_API_LOGGER_METHODS and method not in self.DRF_API_LOGGER_METHODS:
            return response

        content_type = response.get("content-type", "")
        if not content_type.startswith(("application/json", "application/vnd.api+json")):
            return response

        try:
            if getattr(response, "streaming", False):
                response_body = "** Streaming **"
            elif isinstance(response.content, bytes):
                response_body = json.loads(response.content.decode())
            else:
                response_body = json.loads(response.content)
        except Exception:
            response_body = {}

        api = request.get_full_path()

        user = request.user if request.user.is_authenticated else None

        headers = get_headers(request)
        ip = get_client_ip(request)

        data = {
            "api": mask_sensitive_data(api, mask_api_parameters=True),
            "headers": json.dumps(mask_sensitive_data(headers), ensure_ascii=False),
            "body": json.dumps(mask_sensitive_data(request_data), ensure_ascii=False),
            "method": method,
            "client_ip_address": ip,
            "response": json.dumps(mask_sensitive_data(response_body), ensure_ascii=False),
            "status_code": response.status_code,
            "execution_time": time.time() - start_time,
            "added_on": timezone.now(),
            "user": user,
        }

        if self.DRF_API_LOGGER_DATABASE and LOGGER_THREAD:
            try:
                LOGGER_THREAD.put_log_data(data)
            except Exception as e:
                logging.error(
                    "APILoggerMiddleware LOGGER_THREAD error: %s", repr(e)
                )

        if self.DRF_API_LOGGER_SIGNAL:
            try:
                API_LOGGER_SIGNAL.listen(**data)
            except Exception as e:
                logging.error(
                    "APILoggerMiddleware SIGNAL error: %s", repr(e)
                )

        return response

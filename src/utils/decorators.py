from atlas_utils.common.exceptions import BaseError

from logger import app_logger
from utils.ujson_response import google_json_response


def handle_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            app_logger.error(e)

    return wrapper


def error_processing(api_version):
    def decorator(fn):
        def wrapper(request, *args, **kwargs):
            try:
                return fn(request, *args, **kwargs)
            except Exception as error:
                if isinstance(error, BaseError):
                    app_logger.debug(error)
                    return google_json_response(api_version=api_version, status=error.status_code, error=error)
                else:
                    app_logger.exception(error)
                    return google_json_response(api_version=api_version, status=500, error="Внутренняя ошибка сервиса")

        return wrapper

    return decorator

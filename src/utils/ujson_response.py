from atlas_utils.common import exceptions
from atlas_utils.common.ujson_encoder import UJsonEncoder
from django.http import JsonResponse


def _convert_error(error):
    if isinstance(error, exceptions.BaseError):
        return {
            "code": error.status_code,
            "message": error.message if hasattr(error, "message") else type(error).__name__,
            "errors": error.errors,
        }
    else:
        return {"code": 500, "message": "Неизвестная ошибка", "errors": [str(error)]}


def google_json_response(api_version, status, data=None, error=None):
    json = {"apiVersion": api_version}

    if data:
        json["data"] = data
    elif error:
        json["error"] = _convert_error(error)
    else:
        pass

    return JsonResponse(json, encoder=UJsonEncoder, status=status, safe=False)

import logging
import ujson
from typing import Any, Dict, Tuple, Iterator, Optional, Union
from urllib.parse import urljoin

from requests import RequestException, Session
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

logger = logging.getLogger(__name__)

__all__ = ('RequestException', 'JsonDecodeError', 'BaseClient')


class JsonDecodeError(ValueError):
    pass


class BaseClient:
    """Обёртка над библиотекой requests"""

    def __init__(self, base_url: str, timeout: Tuple[float, float], session: Optional[Session] = None,
                 session_retry_params: Optional[Dict] = None):
        """Конструктор клиента

        :param base_url: адрес типа http://example.com или http://example.com/foo/bar/
        :param timeout: таймаут, который по-умолчанию будет определен для каждого запроса
        """
        self._base_url = base_url
        if not base_url.endswith('/'):
            self._base_url += '/'  # это очень важно, если base_url содержит кроме домена еще и путь
        self._timeout = timeout
        self._session = session if session else self._spawn_session_with_retries(session_retry_params)

    def _get(self, endpoint: str, **kwargs) -> Union[dict, Iterator[str]]:
        """GET запрос. Может возбудить исключения RequestException, JsonDecodeError

        :param endpoint: часть адреса, которая склеивается с _base_url
        :param kwargs: аргументы для передачи в запрос, передаются как есть в request
        :return: словать или генератор словарей, если запросили стрим
        """
        return self._request('get', endpoint, **kwargs)

    def _post(self, endpoint: str, **kwargs) -> Union[dict, Iterator[str]]:
        """POST запрос. Может возбудить исключения RequestException, JsonDecodeError

        :param endpoint: часть адреса, которая склеивается с _base_url
        :param kwargs: аргументы для передачи в запрос, передаются как есть в request
        :return: словать или генератор словарей, если запросили стрим
        """
        return self._request('post', endpoint, **kwargs)

    def _delete(self, endpoint: str, **kwargs) -> Union[dict, Iterator[str]]:
        """POST запрос. Может возбудить исключения RequestException, JsonDecodeError

        :param endpoint: часть адреса, которая склеивается с _base_url
        :param kwargs: аргументы для передачи в запрос, передаются как есть в request
        :return: словать или генератор словарей, если запросили стрим
        """
        return self._request('delete', endpoint, **kwargs)

    @staticmethod
    def _spawn_session_with_retries(session_retry_params: Optional[Dict[str, Any]]):
        if not session_retry_params:
            session_retry_params = {
                'total': 3,
                'read': 3,
                'connect': 3,
                'backoff_factor': 1,
                'status_forcelist': (500, 503, 502, 504),
            }
        s = Session()
        retry = Retry(
            **session_retry_params
        )
        adapter = HTTPAdapter(max_retries=retry)
        s.mount('http://', adapter)
        s.mount('https://', adapter)
        return s

    def _request(self, method: str, endpoint: str, **kwargs):
        kwargs.setdefault('timeout', self._timeout)
        url = self._get_url(endpoint)
        logger.info('%s, %s', url, kwargs)
        response = self._session.request(method, url, **kwargs)
        response.raise_for_status()
        if kwargs.get('stream'):
            return _get_stream(response, url, kwargs)
        return _get_json(response.text)

    def _get_url(self, endpoint: str):
        return urljoin(self._base_url, endpoint.lstrip('/'))


def _get_json(text):
    try:
        return ujson.loads(text)
    except ValueError as e:
        raise JsonDecodeError from e


def _get_stream(response, url, request_kwargs):
    for line in response.iter_lines():
        if line:
            try:
                decoded_line = _get_json(line)
            except JsonDecodeError:
                logger.exception('Невалидный JSON в стриме %s',
                                 url,
                                 extra={'request_kwargs': request_kwargs})
            else:
                yield decoded_line

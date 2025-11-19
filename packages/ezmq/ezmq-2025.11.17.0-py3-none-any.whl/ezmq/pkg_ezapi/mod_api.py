import hashlib
import inspect
import json
import re
import time
from pathlib import Path
from typing import Any
from uuid import UUID

import httpx
from annotated_dict import AnnotatedDict
from . import Job, Resource, Jobs, Executor, Response, Message
from . import log, MessageQueue, Response
from .. import JSONLResource, JSONResource

REQUEST_DEFAULTS = {
    "params": {},
    "json": {},
    "headers": {}
}


class RequestHash(AnnotatedDict):
    method: str
    url: str
    params: dict
    json: dict
    headers: dict

    @classmethod
    def from_request(cls, **kwargs) -> 'RequestHash':
        if (not kwargs.get('method')) or (not kwargs.get('url')): raise KeyError(
            f'Missing either method or url, got {kwargs} instead')
        kwargs = REQUEST_DEFAULTS.copy() | kwargs
        instance = cls(**kwargs)
        return instance

    @property
    def hash_key(self) -> str:
        hash_data = {
            'method': self.method,
            'url': self.url,
            'params': self.params,
            'json': self.json,
            'headers': self.headers
        }
        json_str = json.dumps(hash_data, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()


class CacheEntry(AnnotatedDict):
    entry_time: int
    ttl: int = 604800
    method: str
    url: str
    params: dict = {}
    json: dict = {}
    headers: dict = {}
    response: dict
    hash_key: str = ""

    def __post_init__(self):
        if not self.hash_key and self.method and self.url:
            self.hash_key = self._compute_hash()

    def _compute_hash(self):
        request_hash = RequestHash(
            method=self.method,
            url=self.url,
            params=self.params,
            json=self.json,
            headers=self.headers
        )
        return request_hash.hash_key

    @classmethod
    def fetch(cls, hash_key: str, cache: list[dict]) -> 'CacheEntry':
        for entry in cache:
            if entry.get('hash_key') == hash_key:
                return cls(**entry)
        return None

    @staticmethod
    def is_in_cache(hash_key: str, cache: list[dict]) -> bool:
        return any(entry.get('hash_key') == hash_key for entry in cache)

    def commit(self, cache: list[dict]):
        if not self.response:
            raise KeyError("Can't commit without a response field!")

        for i, entry in enumerate(cache):
            if entry.get('hash_key') == self.hash_key:
                cache[i] = {**self}
                return

        cache.append({**self})

    @classmethod
    def from_kwargs(cls, **kwargs):
        if not kwargs.get("response"):
            raise KeyError("Can't construct a cache entry without a response field!")

        instance = cls()
        instance.ttl = kwargs.get("ttl", cls.ttl)
        instance.entry_time = int(time.time())
        instance.method = kwargs.get('method', 'GET')
        instance.url = kwargs.get('url', '')
        instance.params = kwargs.get('params', {})
        instance.json = kwargs.get('json', {})
        instance.headers = kwargs.get('headers', {})
        instance.response = kwargs.get('response')
        instance.hash_key = instance._compute_hash()
        return instance


class RequestJob(Job):
    required_resources = ["api_cache"]
    method: str
    url: str
    params: dict = {}
    json: dict = {}
    headers: dict = {}

    def __init__(self):
        Job.__init__(self)

    def __repr__(self):
        return f"[{self.__class__.__name__}]"

    def execute(self, resources: dict[str, Resource], **kwargs):
        start_time = time.perf_counter()
        default_kwargs = {}
        for key, value in inspect.getmembers(self.__class__):
            if key.startswith("_"): continue
            if callable(value): continue
            if key in ["required_resources"]: continue
            if not isinstance(value, type): default_kwargs[key] = value

        template_pattern = r'\$\{([^}]+)\}'

        for key, value in default_kwargs.items():
            if isinstance(value, str):
                matches = re.findall(template_pattern, value)
                for match in matches:
                    if match in kwargs:
                        value = value.replace(f'${{{match}}}', str(kwargs.pop(match)))
                default_kwargs[key] = value
            elif isinstance(value, dict):
                for dict_key, dict_value in value.items():
                    if isinstance(dict_value, str):
                        matches = re.findall(template_pattern, dict_value)
                        for match in matches:
                            if match in kwargs:
                                dict_value = dict_value.replace(f'${{{match}}}', str(kwargs.pop(match)))
                        value[dict_key] = dict_value

        kwargs = default_kwargs | kwargs

        try:
            cache = resources["api_cache"].peek()
            hash_key = RequestHash.from_request(**kwargs).hash_key

            if not (cache_entry := CacheEntry.fetch(hash_key, cache)):
                try:
                    log.warning(f"{self}: Couldn't find a request to '{kwargs['url']}' in the cache...")
                    log.info(f"{self}: Making '{kwargs['method'].lower()}' request to {kwargs['url']}"
                             f"\n  - params: {kwargs['params']}"
                             f"\n  - json: {kwargs['json']}"
                             f"\n  - headers: {kwargs['headers']}")

                    response = httpx.request(
                        method=kwargs["method"],
                        url=kwargs["url"],
                        params=kwargs["params"],
                        json=kwargs["json"],
                        headers=kwargs["headers"],
                    )
                    response.raise_for_status()

                    if response.is_success:
                        log.debug(f"{self}: Successfully made request to '{kwargs['url']}'")
                    else:
                        log.warning(f"{self}: Failed to make request to '{kwargs['url']}': {response.text}")

                    try:
                        kwargs["response"] = response.json()
                    except (json.JSONDecodeError, ValueError):
                        kwargs["response"] = {
                            "text": response.text,
                            "status_code": response.status_code,
                            "headers": dict(response.headers)
                        }

                except httpx.HTTPStatusError as e:
                    raise Exception(f"Failed to make request to '{kwargs['url']}': {e}")
                except httpx.RequestError as e:
                    raise Exception(f"Failed to make request to '{kwargs.get('url', 'unknown')}': {e}")
                except Exception as e:
                    raise Exception(f"Unexpected error for '{kwargs.get('url', 'unknown')}': {e}")

                try:
                    cache_entry = CacheEntry.from_kwargs(**kwargs)
                    with resources["api_cache"] as c:
                        cache_entry.commit(c)

                    if CacheEntry.is_in_cache(cache_entry.hash_key, resources["api_cache"].peek()):
                        log.info(f"{self}: Successfully cached request as '{cache_entry.hash_key}'")

                    end_time = time.perf_counter()
                    duration = end_time - start_time
                    log.debug(f"{self}: Executed fresh request in: {duration:.4f} seconds")
                    return cache_entry.response

                except Exception as e:
                    raise Exception(f"Error caching request for '{self.url}': {e}")

            else:
                end_time = time.perf_counter()
                duration = end_time - start_time
                log.debug(f"{self}: Retrieved from cache in: {duration:.4f} seconds")
                return cache_entry.response

        except Exception as e:
            raise Exception


class APICache(JSONLResource):
    def __init__(self, identifier: str = None, cwd: Path = Path.cwd()):
        if not identifier:
            identifier = self.__class__.__name__.lower()
        identifier = f"{identifier}-api-cache"
        super().__init__(identifier, cwd)


class RequestJobs(Jobs):
    def __init__(self, identifier: str = None, cwd: Path = Path.cwd()):
        if not identifier:
            identifier = self.__class__.__name__.lower()
        self.identifier = identifier
        if "api_cache" not in self.resources:
            self.resources["api_cache"] = APICache(identifier, cwd)
        super().__init__()
        log.debug(f"{self}: Initialized with {len(self.types)} jobs and {len(self.resources)} resources for API Calls")

    def __repr__(self):
        return f"[{self.__class__.__name__}.RequestJobs]"


class RequestMessageQueue(MessageQueue):
    def __init__(self, job_types: type[RequestJobs], executor: type[Executor] = Executor, auto_start: bool = True):
        super().__init__(job_types, executor, auto_start)


class APIClient:
    headers = {}
    job_types: type[RequestJobs]
    auto_start: bool = True

    def __init__(self):
        if self.__class__.__name__ == "APIClient":
            raise RuntimeError("APIClient cannot be instantiated directly, it must be inherited")

        self.header_deviations: dict[str, dict[str, str]] = {}
        for job_name, job_type in self.job_types.__annotations__.items():
            job_type: RequestJob
            for pointer in job_type.__dict__:
                if pointer == "headers":
                    log.debug(f"{self}: Identified header deviation from default in job type '{job_type.__name__}'")
                    self.header_deviations[job_name] = job_type.__dict__[pointer]

        if not self.job_types:
            raise AttributeError("No job_types referenced")

        self.mq = RequestMessageQueue(self.job_types, executor=Executor, auto_start=self.auto_start)

    def __repr__(self):
        return f"[{self.__class__.__name__}.APIClient]"

    def _compile_headers(self, job_type, **kwargs):
        if not job_type in self.header_deviations:
            headers = self.headers
            if kwargs.get("headers"):
                headers = self.headers | kwargs["headers"]
            else:
                kwargs = {"headers": headers} | kwargs
        return kwargs

    def request(self, job_type: str, **kwargs) -> UUID:
        kwargs = self._compile_headers(job_type, **kwargs)
        return self.mq.send(job_type, **kwargs)

    def response(self, request_id: UUID) -> Response:
        return self.mq.receive(request_id)

    def request_and_response(self, job_type: str, timeout: int = 10, **kwargs) -> Response:
        kwargs = self._compile_headers(job_type, **kwargs)
        return self.mq.send_and_receive(job_type, timeout, **kwargs)

    def batch_request(self, messages: dict[str, Message]) -> dict[str, UUID]:
        for message in messages.values():
            if not message.get("payload"): continue
            message["payload"] = self._compile_headers(message.job_type, **message.payload)
        return self.mq.batch_send(messages)

    def batch_response(self, message_ids: dict[str, UUID], min_timeout: float = 1.0, max_iteration: int = 10) -> tuple[
        dict[str, Response], dict[str, Response]]:
        return self.mq.batch_receive(message_ids, min_timeout, max_iteration)

    def batch_request_and_response(self, messages: dict[str, Message], min_timeout: float = 1.0,
                                   max_iteration: int = 10):
        for message in messages.values():
            if not message.get("payload"): continue
            message["payload"] = self._compile_headers(message.job_type, **message.payload)
        return self.mq.batch_send_and_receive(messages, min_timeout=min_timeout, max_iteration=max_iteration)


import json
import time
import threading
from pathlib import Path
from uuid import UUID

import pytest
import httpx
from unittest.mock import Mock, patch

from ezmq import Job, Jobs, Executor, Response

@pytest.fixture
def temp_dir(tmp_path):
    return tmp_path


@pytest.fixture
def api_cache(temp_dir):
    return APICache("test_api", cwd=temp_dir)


@pytest.fixture
def mock_response():
    response = Mock(spec=httpx.Response)
    response.is_success = True
    response.status_code = 200
    response.json.return_value = {"data": "test_data", "status": "success"}
    response.text = '{"data": "test_data", "status": "success"}'
    response.headers = {"content-type": "application/json"}
    return response


class TestRequestHash:
    def test_from_request_basic(self):
        hash_obj = RequestHash.from_request(method="GET", url="https://api.example.com")
        assert hash_obj.method == "GET"
        assert hash_obj.url == "https://api.example.com"
        assert hash_obj.params == {}
        assert hash_obj.json == {}
        assert hash_obj.headers == {}

    def test_from_request_with_params(self):
        hash_obj = RequestHash.from_request(
            method="POST",
            url="https://api.example.com/users",
            params={"page": 1},
            json={"name": "test"},
            headers={"Authorization": "Bearer token"}
        )
        assert hash_obj.params == {"page": 1}
        assert hash_obj.json == {"name": "test"}
        assert hash_obj.headers == {"Authorization": "Bearer token"}

    def test_from_request_missing_method(self):
        with pytest.raises(KeyError):
            RequestHash.from_request(url="https://api.example.com")

    def test_from_request_missing_url(self):
        with pytest.raises(KeyError):
            RequestHash.from_request(method="GET")

    def test_hash_key_deterministic(self):
        hash1 = RequestHash.from_request(method="GET", url="https://api.example.com")
        hash2 = RequestHash.from_request(method="GET", url="https://api.example.com")
        assert hash1.hash_key == hash2.hash_key

    def test_hash_key_different_params(self):
        hash1 = RequestHash.from_request(
            method="GET",
            url="https://api.example.com",
            params={"page": 1}
        )
        hash2 = RequestHash.from_request(
            method="GET",
            url="https://api.example.com",
            params={"page": 2}
        )
        assert hash1.hash_key != hash2.hash_key

    def test_hash_key_same_params_different_order(self):
        hash1 = RequestHash.from_request(
            method="GET",
            url="https://api.example.com",
            params={"a": 1, "b": 2}
        )
        hash2 = RequestHash.from_request(
            method="GET",
            url="https://api.example.com",
            params={"b": 2, "a": 1}
        )
        assert hash1.hash_key == hash2.hash_key


class TestCacheEntry:
    def test_from_kwargs_basic(self):
        entry = CacheEntry.from_kwargs(
            method="GET",
            url="https://api.example.com",
            response={"data": "test"}
        )
        assert entry.method == "GET"
        assert entry.url == "https://api.example.com"
        assert entry.response == {"data": "test"}
        assert entry.hash_key

    def test_from_kwargs_without_response(self):
        with pytest.raises(KeyError):
            CacheEntry.from_kwargs(method="GET", url="https://api.example.com")

    def test_from_kwargs_with_custom_ttl(self):
        entry = CacheEntry.from_kwargs(
            method="GET",
            url="https://api.example.com",
            response={"data": "test"},
            ttl=3600
        )
        assert entry.ttl == 3600

    def test_commit_to_empty_cache(self):
        cache = []
        entry = CacheEntry.from_kwargs(
            method="GET",
            url="https://api.example.com",
            response={"data": "test"}
        )
        entry.commit(cache)
        assert len(cache) == 1
        assert cache[0]["hash_key"] == entry.hash_key

    def test_commit_updates_existing(self):
        cache = []
        entry1 = CacheEntry.from_kwargs(
            method="GET",
            url="https://api.example.com",
            response={"data": "old"}
        )
        entry1.commit(cache)

        entry2 = CacheEntry.from_kwargs(
            method="GET",
            url="https://api.example.com",
            response={"data": "new"}
        )
        entry2.commit(cache)

        assert len(cache) == 1
        assert cache[0]["response"]["data"] == "new"

    def test_fetch_existing(self):
        cache = []
        entry = CacheEntry.from_kwargs(
            method="GET",
            url="https://api.example.com",
            response={"data": "test"}
        )
        entry.commit(cache)

        fetched = CacheEntry.fetch(entry.hash_key, cache)
        assert fetched is not None
        assert fetched.response == {"data": "test"}

    def test_fetch_nonexistent(self):
        cache = []
        fetched = CacheEntry.fetch("nonexistent_hash", cache)
        assert fetched is None

    def test_is_in_cache(self):
        cache = []
        entry = CacheEntry.from_kwargs(
            method="GET",
            url="https://api.example.com",
            response={"data": "test"}
        )
        entry.commit(cache)

        assert CacheEntry.is_in_cache(entry.hash_key, cache)
        assert not CacheEntry.is_in_cache("nonexistent", cache)

    def test_commit_without_response(self):
        cache = []
        entry = CacheEntry(
            method="GET",
            url="https://api.example.com",
            entry_time=int(time.time())
        )
        with pytest.raises(KeyError):
            entry.commit(cache)


class TestAPICache:
    def test_initialization(self, temp_dir):
        cache = APICache("test", cwd=temp_dir)
        assert cache.identifier == "test-api-cache"
        assert cache.file_path.name == "test-api-cache.jsonl"

    def test_read_write(self, temp_dir):
        cache = APICache("test", cwd=temp_dir)

        with cache as data:
            data.append({"key": "value1"})
            data.append({"key": "value2"})

        peeked = cache.peek()
        assert len(peeked) == 2
        assert peeked[0]["key"] == "value1"
        assert peeked[1]["key"] == "value2"

    def test_persistence(self, temp_dir):
        cache1 = APICache("test", cwd=temp_dir)
        with cache1 as data:
            data.append({"persistent": "data"})

        cache2 = APICache("test", cwd=temp_dir)
        peeked = cache2.peek()
        assert len(peeked) == 1
        assert peeked[0]["persistent"] == "data"


class TestRequestJob:
    def test_job_initialization(self):
        job = RequestJob()
        assert "api_cache" in job.required_resources

    def test_template_substitution(self, api_cache, mock_response):
        class TestJob(RequestJob):
            method = "GET"
            url = "https://api.example.com/users/${user_id}"
            params = {"filter": "${filter_value}"}

        job = TestJob()
        resources = {"api_cache": api_cache}

        with patch('httpx.request', return_value=mock_response):
            result = job.execute(resources, user_id="123", filter_value="active")
            assert result == {"data": "test_data", "status": "success"}

    def test_caching_behavior(self, api_cache, mock_response):
        class TestJob(RequestJob):
            method = "GET"
            url = "https://api.example.com/data"

        job = TestJob()
        resources = {"api_cache": api_cache}

        with patch('httpx.request', return_value=mock_response) as mock_request:
            result1 = job.execute(resources)
            result2 = job.execute(resources)

            assert mock_request.call_count == 1
            assert result1 == result2

    def test_http_error_handling(self, api_cache):
        class TestJob(RequestJob):
            method = "GET"
            url = "https://api.example.com/error"

        job = TestJob()
        resources = {"api_cache": api_cache}

        error_response = Mock(spec=httpx.Response)
        error_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404 Not Found",
            request=Mock(),
            response=Mock()
        )

        with patch('httpx.request', return_value=error_response):
            with pytest.raises(Exception):
                job.execute(resources)

    def test_non_json_response(self, api_cache):
        class TestJob(RequestJob):
            method = "GET"
            url = "https://api.example.com/html"

        job = TestJob()
        resources = {"api_cache": api_cache}

        html_response = Mock(spec=httpx.Response)
        html_response.is_success = True
        html_response.status_code = 200
        html_response.json.side_effect = json.JSONDecodeError("msg", "doc", 0)
        html_response.text = "<html>test</html>"
        html_response.headers = {"content-type": "text/html"}
        html_response.raise_for_status = Mock()

        with patch('httpx.request', return_value=html_response):
            result = job.execute(resources)
            assert result["text"] == "<html>test</html>"
            assert result["status_code"] == 200


class TestAPIClient:
    def test_cannot_instantiate_directly(self):
        with pytest.raises(RuntimeError):
            APIClient()

    def test_subclass_initialization(self, temp_dir):
        class GetUserJob(RequestJob):
            method = "GET"
            url = "https://api.example.com/users/${user_id}"

        class TestJobs(RequestJobs):
            get_user: GetUserJob

        class TestClient(APIClient):
            job_types = TestJobs
            headers = {"Authorization": "Bearer test_token"}

        client = TestClient()
        assert client.mq is not None

    def test_request_and_response(self, temp_dir, mock_response):
        class GetDataJob(RequestJob):
            method = "GET"
            url = "https://api.example.com/data"

        class TestJobs(RequestJobs):
            get_data: GetDataJob

            def __init__(self, identifier: str = None, cwd: Path = Path.cwd()):
                super().__init__(identifier, cwd)

        class TestClient(APIClient):
            job_types = TestJobs
            headers = {"Authorization": "Bearer token"}

        with patch('httpx.request', return_value=mock_response):
            client = TestClient()
            request_id = client.request("get_data")
            assert isinstance(request_id, UUID)

            response = client.response(request_id)
            assert response.success == True
            assert response.result == {"data": "test_data", "status": "success"}

    def test_header_compilation(self, temp_dir, mock_response):
        # Generate unique identifier for this test
        import uuid
        test_id = str(uuid.uuid4())[:8]

        class GetDataJob(RequestJob):
            method = "GET"
            url = f"https://api.example.com/data-{test_id}"

        class TestJobs(RequestJobs):
            get_data: GetDataJob

            def __init__(self, identifier: str = None, cwd: Path = Path.cwd()):
                super().__init__(f"headers_test_{test_id}", temp_dir)

        class TestClient(APIClient):
            job_types = TestJobs
            headers = {"Authorization": "Bearer token", "X-Custom": "value"}

        with patch('httpx.request', return_value=mock_response) as mock_request:
            client = TestClient()
            request_id = client.request("get_data")

            time.sleep(0.5)

            call_kwargs = mock_request.call_args.kwargs
            assert "Authorization" in call_kwargs["headers"]
            assert "X-Custom" in call_kwargs["headers"]

    def test_concurrent_requests(self, temp_dir, mock_response):
        class GetDataJob(RequestJob):
            method = "GET"
            url = "https://api.example.com/data/${id}"

        class TestJobs(RequestJobs):
            get_data: GetDataJob

        class TestClient(APIClient):
            job_types = TestJobs

        with patch('httpx.request', return_value=mock_response):
            client = TestClient()

            request_ids = []
            for i in range(10):
                request_id = client.request("get_data", id=str(i))
                request_ids.append(request_id)

            responses = []
            for request_id in request_ids:
                response = client.response(request_id)
                responses.append(response)

            assert len(responses) == 10
            assert all(r.success == True for r in responses)

    def test_batch_request(self, temp_dir, mock_response):
        class GetDataJob(RequestJob):
            method = "GET"
            url = "https://api.example.com/data/${id}"

        class TestJobs(RequestJobs):
            get_data: GetDataJob

        class TestClient(APIClient):
            job_types = TestJobs

        with patch('httpx.request', return_value=mock_response):
            client = TestClient()

            from ezmq import Message
            messages = {}
            for i in range(5):
                msg = Message()
                msg.job_type = "get_data"
                msg.payload = {"id": str(i)}
                messages[f"request_{i}"] = msg

            request_ids = client.batch_request(messages)
            assert len(request_ids) == 5
            assert all(isinstance(uid, UUID) for uid in request_ids.values())


class TestConcurrency:
    def test_thread_safe_caching(self, temp_dir, mock_response):
        class GetDataJob(RequestJob):
            method = "GET"
            url = "https://api.example.com/data"

        class TestJobs(RequestJobs):
            get_data: GetDataJob

        class TestClient(APIClient):
            job_types = TestJobs

        errors = []
        results = []

        def make_request(client):
            try:
                request_id = client.request("get_data")
                response = client.response(request_id)
                results.append(response.result)
            except Exception as e:
                errors.append(e)

        with patch('httpx.request', return_value=mock_response):
            client = TestClient()

            threads = []
            for _ in range(10):
                t = threading.Thread(target=make_request, args=(client,))
                threads.append(t)
                t.start()

            for t in threads:
                t.join()

        assert not errors
        assert len(results) == 10
        assert all(r == results[0] for r in results)

    def test_concurrent_different_requests(self, temp_dir):
        class GetDataJob(RequestJob):
            method = "GET"
            url = "https://api.example.com/data/${id}"

        class TestJobs(RequestJobs):
            get_data: GetDataJob

        class TestClient(APIClient):
            job_types = TestJobs

        def mock_request_func(**kwargs):
            response = Mock(spec=httpx.Response)
            response.is_success = True
            response.status_code = 200

            url = kwargs.get('url', '')
            data_id = url.split('/')[-1] if '/' in url else '0'
            response.json.return_value = {"id": data_id, "data": f"data_{data_id}"}
            response.raise_for_status = Mock()
            return response

        errors = []
        results = {}

        def make_request(client, request_id):
            try:
                uuid = client.request("get_data", id=str(request_id))
                response = client.response(uuid)
                results[request_id] = response.result
            except Exception as e:
                errors.append((request_id, e))

        with patch('httpx.request', side_effect=mock_request_func):
            client = TestClient()

            threads = []
            for i in range(20):
                t = threading.Thread(target=make_request, args=(client, i))
                threads.append(t)
                t.start()

            for t in threads:
                t.join()

        assert not errors
        assert len(results) == 20


class TestCacheEviction:
    def test_ttl_stored(self, temp_dir):
        cache = APICache("test", cwd=temp_dir)

        entry = CacheEntry.from_kwargs(
            method="GET",
            url="https://api.example.com/data",
            response={"data": "test"},
            ttl=3600
        )

        with cache as c:
            entry.commit(c)

        cached = cache.peek()
        assert cached[0]["ttl"] == 3600

    def test_entry_time_recorded(self, temp_dir):
        cache = APICache("test", cwd=temp_dir)

        before = int(time.time())
        entry = CacheEntry.from_kwargs(
            method="GET",
            url="https://api.example.com/data",
            response={"data": "test"}
        )
        after = int(time.time())

        assert before <= entry.entry_time <= after


class TestEdgeCases:
    def test_empty_cache_file(self, temp_dir):
        cache = APICache("test", cwd=temp_dir)
        cache.file_path.touch()

        peeked = cache.peek()
        assert peeked == []

    def test_corrupted_cache_line(self, temp_dir):
        cache = APICache("test", cwd=temp_dir)

        with cache as c:
            c.append({"valid": "entry1"})

        with cache.file_path.open('a') as f:
            f.write('{"invalid": json\n')

        with cache as c:
            c.append({"valid": "entry2"})

        peeked = cache.peek()
        assert len(peeked) >= 2
        assert any(e.get("valid") == "entry1" for e in peeked)
        assert any(e.get("valid") == "entry2" for e in peeked)

    def test_large_response_body(self, temp_dir, mock_response):
        large_data = {"data": "x" * 100000}
        mock_response.json.return_value = large_data

        class GetDataJob(RequestJob):
            method = "GET"
            url = "https://api.example.com/large"

        job = GetDataJob()
        cache = APICache("test", cwd=temp_dir)
        resources = {"api_cache": cache}

        with patch('httpx.request', return_value=mock_response):
            result = job.execute(resources)
            assert result == large_data

            cached = cache.peek()
            assert len(cached) == 1
            assert cached[0]["response"] == large_data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
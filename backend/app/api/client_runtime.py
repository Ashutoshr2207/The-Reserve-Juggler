"""Contract-driven HTTP client support. Generated methods contain no second schema."""
import re
from urllib.parse import quote

from app.api.contracts import CONTRACT, validate


class ContractClient:
    def __init__(self, transport):
        # An httpx.Client or TestClient with the authenticated local cookie/CSRF.
        self.transport = transport

    def call(self, operation_id, *, path=None, body=None, files=None, headers=None, query=None):
        route, method, operation = next(
            (route, method, operation)
            for route, methods in CONTRACT['paths'].items() for method, operation in methods.items()
            if operation['operationId'] == operation_id)
        path = path or {}
        required = set(re.findall(r'\{([^}]+)\}', route))
        if set(path) != required:
            raise ValueError('Path parameters do not match the contract')
        for name, value in path.items():
            route = route.replace('{' + name + '}', quote(str(value), safe=''))
        request_content = operation.get('requestBody', {}).get('content', {})
        if 'application/json' in request_content:
            reference = request_content['application/json']['schema']['$ref']
            validate(reference.rsplit('/', 1)[-1], body)
        kwargs = {'headers': headers, 'params': query}
        if body is not None:
            kwargs['json'] = body
        if files is not None:
            kwargs['files'] = files
        response = self.transport.request(method.upper(), '/api/v1' + route, **kwargs)
        response_spec = operation['responses'].get(str(response.status_code))
        if not response_spec:
            raise RuntimeError('Undocumented response status')
        reference = response_spec['content']['application/json']['schema']['$ref']
        validate(reference.rsplit('/', 1)[-1], response.json(), output=True)
        return response

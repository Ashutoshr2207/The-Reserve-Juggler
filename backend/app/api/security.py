"""Local OS bootstrap and ephemeral session. No remote identity claims."""
import secrets
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from app.api.contracts import ROOT, Problem


@dataclass(frozen=True)
class Config:
    runtime: Path = ROOT / 'work/runtime'
    origin: str = 'http://127.0.0.1:8000'
    role: str = 'operator'
    frontend_origin: str | None = None

    def __post_init__(self):
        if self.role not in ('operator', 'maker', 'reviewer', 'auditor'):
            raise ValueError('Unsupported startup role')
        runtime = Path(self.runtime).resolve()
        if not runtime.is_relative_to(ROOT.resolve()):
            raise ValueError('Runtime must remain in backend')
        object.__setattr__(self, 'runtime', runtime)
        for origin in (self.origin, self.frontend_origin):
            if origin is None:
                continue
            url = urlsplit(origin)
            if (url.scheme != 'http' or url.hostname not in ('127.0.0.1', 'localhost')
                    or url.username or url.password or url.path or url.query or url.fragment):
                raise ValueError('Only exact loopback HTTP origins are supported')


class LocalSession:
    def __init__(self, config, now=time.monotonic):
        self.config, self.now = config, now
        self.bootstrap = secrets.token_urlsafe(48)
        self.token = secrets.token_urlsafe(48)
        self.csrf = secrets.token_urlsafe(32)
        self.last_used = now()
        self.active = False

    def check_host(self, request):
        if request.headers.get('host') != urlsplit(self.config.origin).netloc:
            raise Problem(403, 'FORBIDDEN', 'Invalid local host.')
        if request.client is None or request.client.host not in ('127.0.0.1', '::1'):
            raise Problem(403, 'FORBIDDEN', 'Loopback access is required.')
        fetch_site = request.headers.get('sec-fetch-site')
        if fetch_site == 'cross-site':
            raise Problem(403, 'FORBIDDEN', 'Cross-site access is denied.')

    def authenticate(self, request):
        supplied = request.cookies.get('rg_session', '')
        if self.active and self.now() - self.last_used >= 8 * 3600:
            self.active, self.token = False, None
        if not self.active or not self.token or not secrets.compare_digest(supplied, self.token):
            raise Problem(401, 'UNAUTHORIZED', 'A current local session is required.')
        origin = request.headers.get('origin')
        allowed = {self.config.origin, self.config.frontend_origin} - {None}
        if origin is not None and origin not in allowed:
            raise Problem(403, 'FORBIDDEN', 'Origin is not allowed.')
        if request.method not in ('GET', 'HEAD', 'OPTIONS'):
            if origin not in allowed or not secrets.compare_digest(request.headers.get('x-csrf-token', ''), self.csrf):
                raise Problem(403, 'FORBIDDEN', 'Mutation requires the local origin and CSRF token.')
        self.last_used = self.now()

    def role(self, operation):
        from app.api.contracts import CONTRACT
        allowed = next(op['x-local-roles'] for methods in CONTRACT['paths'].values()
                       for op in methods.values() if op['operationId'] == operation)
        if self.config.role not in allowed:
            raise Problem(403, 'FORBIDDEN', 'Local role cannot perform this action.')

    def exchange(self, capability):
        if not self.bootstrap or not secrets.compare_digest(capability, self.bootstrap):
            raise Problem(401, 'UNAUTHORIZED', 'Invalid or consumed local bootstrap.')
        self.bootstrap = None
        self.active = True
        self.last_used = self.now()

    def revoke(self):
        self.active, self.token = False, None

"""Single-process loopback launcher; bootstrap capability never goes in logs."""
import os
import webbrowser
from threading import Timer

import uvicorn

from app.api.application import create_app
from app.api.security import Config


def main():
    port = int(os.environ.get('RG_PORT', '8000'))
    if not 1 <= port <= 65535:
        raise ValueError('RG_PORT must be between 1 and 65535')
    config = Config(role=os.environ.get('RG_ROLE_MODE', 'operator'),
                    origin=f'http://127.0.0.1:{port}',
                    frontend_origin=os.environ.get('RG_FRONTEND_ORIGIN') or None)
    app = create_app(config)
    url = config.origin + '/local/session#' + app.state.session.bootstrap
    timer = Timer(1.5, lambda: webbrowser.open(url))
    timer.daemon = True
    timer.start()
    uvicorn.run(app, host='127.0.0.1', port=port, workers=1, access_log=False, proxy_headers=False)


if __name__ == '__main__':
    main()

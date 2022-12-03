"""
    Author Zotov Nikita
"""

import threading

from werkzeug.serving import make_server

from log import get_default_logger
from server.frontend.app import Application
from server.frontend.configurator import BaseConfigurator


logger = get_default_logger(__name__)


class ServerThread(threading.Thread):
    def __init__(self, app: Application):
        threading.Thread.__init__(self)
        logger.info("Initialize server thread")
        self.server = make_server(str(app.ip), app.port, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()


class Server:
    def __init__(self, app: Application):
        self._app = app
        self._thread = None

    def start(self, configurator: BaseConfigurator):
        self._app.prepare(configurator)
        self._thread = ServerThread(self._app)
        self._thread.start()

        logger.info(f"Start server on route [{self._app.ip}:{self._app.port}]")

    def stop(self):
        self._thread.shutdown()
        self._thread = None

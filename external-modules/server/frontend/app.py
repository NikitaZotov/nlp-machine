"""
    Author Zotov Nikita
"""

from flask import Flask
from flask_cors import CORS
from log import get_default_logger

from json_client import client
from modules.lexical_analysis_module.module import LexicalAnalysisModule
from modules.sentence_analysis_module.module import SentenceAnalysisModule
from server.frontend.configurator import BaseConfigurator

logger = get_default_logger(__name__)
cors = CORS()


class Application(Flask):
    def __init__(self, configurator: BaseConfigurator):
        super().__init__(__name__, template_folder='templates')
        cors.init_app(self)
        self.configurator = configurator

    def start(self) -> None:
        self.prepare()
        self.run(host=str(self.configurator.flask_ip), port=self.configurator.flask_port, debug=False)

    def prepare(self) -> None:
        platform_base_url = f"ws://{self.configurator.platform_ip}:{self.configurator.platform_port}/"
        platform_url = platform_base_url + self.configurator.platform_url_path

        client.connect(platform_url)
        if not client.is_connected():
            raise ConnectionAbortedError("Please start platform server first")
        else:
            LexicalAnalysisModule()
            SentenceAnalysisModule()

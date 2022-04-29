"""
    Author Zotov Nikita
"""

from flask import Flask
from flask_cors import CORS
from log import get_default_logger

from json_client import client
from modules.lexical_analysis_module.module import LexicalAnalysisModule
from modules.semantic_analysis_module.module import SemanticAnalysisModule
from modules.sentence_analysis_module.module import SentenceAnalysisModule
from modules.syntactic_analysis_module.module import SyntacticAnalysisModule
from server import params
from server.frontend.configurator import BaseConfigurator

logger = get_default_logger(__name__)
cors = CORS()


class Application(Flask):
    def __init__(self):
        super().__init__(__name__, template_folder='templates')
        cors.init_app(self)
        self.secret_key = "nlp-ostis"
        self.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
        self.config['UPLOAD_FOLDER'] = '/home/nikita/'

        self.ip: str = ""
        self.port: int = 0

    def prepare(self, configurator: BaseConfigurator) -> None:
        self.ip = configurator.flask_ip
        self.port = configurator.flask_port

        platform_base_url = f"ws://{configurator.platform_ip}:{configurator.platform_port}/"
        platform_url = platform_base_url + configurator.platform_url_path

        client.connect(platform_url)
        if not client.is_connected():
            raise ConnectionAbortedError("Please start platform server first")
        else:
            LexicalAnalysisModule()
            SentenceAnalysisModule()
            SyntacticAnalysisModule()
            SemanticAnalysisModule()

    def get_server_url(self):
        return f"{params.HTTP}{self.ip}:{self.port}"

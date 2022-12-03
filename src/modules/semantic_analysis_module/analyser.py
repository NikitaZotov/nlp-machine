"""
    Author Zotov Nikita
"""

from nltk import CoreNLPDependencyParser

from json_client import client
from json_client.dataclass import ScAddr
from log import get_default_logger
from modules.semantic_analysis_module.synthesizer import SemanticSynthesizer

logger = get_default_logger(__name__)


class SemanticAnalyser:
    def __init__(self):
        self._forms_lexemes = {}

        self._synthesizer = SemanticSynthesizer()

    def analyse(self, text_link_addr: ScAddr) -> ScAddr:
        text = client.get_link_content(text_link_addr).data

        parser = CoreNLPDependencyParser()
        graph = next(parser.raw_parse(text))

        return self._synthesizer.synthesize(graph, text_link_addr)

"""
    Author Zotov Nikita
"""

from nltk import CoreNLPParser

from json_client import client
from json_client.dataclass import ScAddr
from log import get_default_logger
from modules.syntactic_analysis_module.synthesizer import SyntacticSynthesizer

logger = get_default_logger(__name__)


class SyntacticAnalyser:
    def __init__(self):
        self._forms_lexemes = {}

        self._synthesizer = SyntacticSynthesizer()

    def analyse(self, text_link_addr: ScAddr) -> ScAddr:
        text = client.get_link_content(text_link_addr).data

        parser = CoreNLPParser()
        parse_tree = next(parser.raw_parse(text))

        return self._synthesizer.synthesize(parse_tree, text_link_addr)

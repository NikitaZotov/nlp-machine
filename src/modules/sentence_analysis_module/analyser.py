"""
    Author Zotov Nikita
"""

from typing import Dict

from json_client.dataclass import ScAddr
from log import get_default_logger
from modules.common.searcher import get_system_idtf
from modules.sentence_analysis_module.synthesizer import SentenceSynthesizer

logger = get_default_logger(__name__)


class SentencesAnalyser:
    def __init__(self):
        self._forms_lexemes = {}

        self._synthesizer = SentenceSynthesizer()

    def analyse(self, text_link_addr: ScAddr, forms_lexemes: Dict[str, str]) -> ScAddr:
        self._forms_lexemes = forms_lexemes

        logger.info("Synthesize text \"" + get_system_idtf(text_link_addr) + "\"")
        return self._synthesizer.synthesize(self._forms_lexemes, text_link_addr)

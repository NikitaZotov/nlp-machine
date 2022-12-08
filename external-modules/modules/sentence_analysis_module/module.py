"""
    Author Zotov Nikita
"""

from json_client.sc_module import ScModule
from modules.sentence_analysis_module.agents import SentencesAnalysisAgent


class SentenceAnalysisModule(ScModule):
    def __init__(self) -> None:
        super().__init__([SentencesAnalysisAgent])

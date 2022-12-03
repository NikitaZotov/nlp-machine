"""
    Author Zotov Nikita
"""

from json_client.sc_module import ScModule
from modules.lexical_analysis_module.agents import LexicalAnalysisAgent, LexicalGrammarAnalysisAgent


class LexicalAnalysisModule(ScModule):
    def __init__(self) -> None:
        super().__init__([LexicalAnalysisAgent, LexicalGrammarAnalysisAgent])

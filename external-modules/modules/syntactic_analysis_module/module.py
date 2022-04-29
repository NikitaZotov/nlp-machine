"""
    Author Zotov Nikita
"""

from json_client.sc_module import ScModule
from modules.syntactic_analysis_module.agents import SyntacticAnalysisAgent


class SyntacticAnalysisModule(ScModule):
    def __init__(self) -> None:
        super().__init__([SyntacticAnalysisAgent])

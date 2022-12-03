"""
    Author Zotov Nikita
"""

from json_client.sc_module import ScModule
from modules.semantic_analysis_module.agents import SemanticAnalysisAgent


class SemanticAnalysisModule(ScModule):
    def __init__(self) -> None:
        super().__init__([SemanticAnalysisAgent])

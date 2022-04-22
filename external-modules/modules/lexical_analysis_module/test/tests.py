"""
    Author Zotov Nikita
"""

import unittest

from json_client import client
from json_client.kb_tests import ScTest
from modules.common.generator import generate_link
from modules.common.identifiers import ActionIdentifiers, QuestionStatus, CommonIdentifiers
from modules.common.utils import complete_agent
from modules.lexical_analysis_module.analyser import LexicalAnalyser
from modules.lexical_analysis_module.module import LexicalAnalysisModule
from modules.lexical_analysis_module.test.text_samples import ontology_sample


class LexicalAnalysisModuleTest(ScTest):
    @classmethod
    def setUpClass(cls) -> None:
        client.connect("ws://localhost:8090/ws_json")
        LexicalAnalysisModule()

    @classmethod
    def tearDownClass(cls) -> None:
        client.disconnect()


class LexicalAnalysisTest(LexicalAnalysisModuleTest):
    def test_analyse_text(self):
        text_link_addr = generate_link(ontology_sample)
        an = LexicalAnalyser()
        an.analyse(text_link_addr)

    def test_call_lexical_grammar_agent(self):
        text_link_addr = generate_link("Ontology is the branch of philosophy that studies concepts such as existence, "
                                       "being, becoming, and reality. It includes the questions of how entities are "
                                       "grouped into basic categories and which of these entities exist on the most "
                                       "fundamental level.")
        idtf_link_addr = generate_link("ontology_sample")

        action, status = complete_agent(
            {text_link_addr: False, idtf_link_addr: False},
            [ActionIdentifiers.ACTION_LEXICAL_GRAMMAR_ANALYSIS_AGENT.value, CommonIdentifiers.QUESTION.value],
            reaction=QuestionStatus.QUESTION_FINISHED_SUCCESSFULLY,
            wait_time=10
        )
        self.assertTrue(status)


if __name__ == "__main__":
    unittest.main()

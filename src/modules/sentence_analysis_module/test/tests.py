"""
    Author Zotov Nikita
"""

import unittest

from json_client.kb_tests import ScTest
from modules.common.generator import generate_link
from modules.sentence_analysis_module.analyser import SentencesAnalyser


class SentencesAnalysisTest(ScTest):
    def test_analyse_text(self):
        text_link_addr = generate_link("Ontology is the branch of philosophy that studies concepts such as existence, "
                                       "being, becoming, and reality. It includes the questions of how entities are "
                                       "grouped into basic categories and which of these entities exist on the most "
                                       "fundamental level.")

        an = SentencesAnalyser()
        an.analyse(text_link_addr, "text_1")


if __name__ == "__main__":
    unittest.main()

"""
    Author Zotov Nikita
"""
import unittest

from nltk import CoreNLPParser

from json_client.kb_tests import ScTest
from modules.common.generator import generate_link
from modules.lexical_analysis_module.test.text_samples import ontology_sample
from modules.syntactic_analysis_module.synthesizer import SyntacticSynthesizer


class SyntacticAnalysisTest(ScTest):
    def test_analyse_text(self):
        # STANFORD = os.path.join("/home/nikita/", "stanford-corenlp-full-2018-02-27")
        #
        # server = CoreNLPServer(
        #     os.path.join(STANFORD, "stanford-corenlp-3.9.1.jar"),
        #     os.path.join(STANFORD, "stanford-corenlp-3.9.1-models.jar"),
        # )

        # server.start()
        parser = CoreNLPParser()
        tree = next(parser.raw_parse(ontology_sample))

        SyntacticSynthesizer().synthesize(tree, generate_link(ontology_sample))

        # server.stop()


if __name__ == "__main__":
    unittest.main()

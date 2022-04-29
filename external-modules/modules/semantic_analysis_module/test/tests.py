"""
    Author Zotov Nikita
"""
import unittest

from nltk import CoreNLPDependencyParser

from json_client.kb_tests import ScTest
from modules.lexical_analysis_module.test.text_samples import ontology_sample
from modules.semantic_analysis_module.synthesizer import SemanticSynthesizer


class SemanticAnalysisTest(ScTest):
    def test_analyse_text(self):
        parser = CoreNLPDependencyParser()
        graph = next(parser.raw_parse(ontology_sample))

        print("{:<15} | {:<10} | {:<10} | {:<15} | {:<10}".format(
            'Head', 'Head POS', 'Relation', 'Dependent', 'Dependent POS')
        )
        print("-" * 75)

        for dep in list(graph.triples()):
            print("{:<15} | {:<10} | {:<10} | {:<15} | {:<10}".format(
                str(dep[0][0]), str(dep[0][1]), str(dep[1]), str(dep[2][0]), str(dep[2][1]))
            )

    #SemanticSynthesizer().synthesize(tree, generate_link(ontology_sample))


if __name__ == "__main__":
    unittest.main()

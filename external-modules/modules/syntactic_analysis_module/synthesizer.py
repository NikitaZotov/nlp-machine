"""
    Author Zotov Nikita
"""

from typing import List

from nltk import Tree

from json_client.constants import sc_types
from json_client.dataclass import ScAddr
from json_client.sc_agent import ScKeynodes
from log import get_default_logger
from modules.common.generator import generate_edge, generate_node, generate_link, wrap_in_set, generate_binary_relation
from modules.lexical_analysis_module.speech_parts import speech_parts
from modules.syntactic_analysis_module.constants import Identifiers
from modules.syntactic_analysis_module.phrases import phrases

logger = get_default_logger(__name__)


class SyntacticSynthesizer:
    def __init__(self):
        self._keynodes = ScKeynodes()
        self.concept_lexeme = self._keynodes.__getitem__(
            Identifiers.CONCEPT_LEXEME.value, sc_types.NODE_CONST_CLASS
        )
        self.nrel_text_decomposition = self._keynodes.__getitem__(
            Identifiers.NREL_TEXT_DECOMPOSITION.value, sc_types.NODE_CONST_NOROLE
        )
        self.nrel_sequence_in_linear_text = self._keynodes.__getitem__(
            Identifiers.NREL_SEQUENCE_IN_LINEAR_TEXT.value, sc_types.NODE_CONST_NOROLE
        )
        self.nrel_syntactic_structure = self._keynodes.__getitem__(
            Identifiers.NREL_SYNTACTIC_STRUCTURE.value, sc_types.NODE_CONST_CLASS
        )
        self._puncts = [',', '.', '!', '?', ';', '-', ':']
        self._next_word_link_addr = ScAddr(0)

    def synthesize(self, tree: Tree, text_link_addr: ScAddr) -> ScAddr:
        sentence = tree[0]
        logger.info(f"Synthesize syntactic tree")

        struct_addr = generate_node(sc_types.NODE_CONST_STRUCT)
        generate_binary_relation(
            text_link_addr, sc_types.EDGE_D_COMMON_CONST, struct_addr, self.nrel_syntactic_structure
        )
        wrap_in_set([self.nrel_text_decomposition, self.nrel_sequence_in_linear_text], struct_addr)

        self._visit_parse_tree(sentence, text_link_addr, struct_addr)
        return struct_addr

    def _visit_parse_tree(self, text: Tree, text_link_addr: ScAddr, struct_addr: ScAddr):
        if len(text) == 0:
            return

        tuple_addr = ScAddr(0)
        for part in text:
            if isinstance(part, str):
                continue

            relation_str = part.label()

            if relation_str in self._puncts:
                continue

            logger.info(f"Synthesize \"{part}\"")

            if not tuple_addr.is_valid():
                tuple_addr = self._resolve_text_decomposition_tuple(text_link_addr, struct_addr)

            part_link_addr = self._resolve_text(part.leaves())
            wrap_in_set([part_link_addr], struct_addr)

            relation_idtf = phrases.get(relation_str)
            class_idtf_list = speech_parts.get(relation_str)
            if relation_idtf is not None:
                relation_addr = self._keynodes.__getitem__(relation_idtf, sc_types.NODE_CONST_ROLE)

                edge = generate_edge(tuple_addr, part_link_addr, sc_types.EDGE_ACCESS_CONST_POS_PERM)
                rrel_edge = generate_edge(
                    relation_addr, edge, sc_types.EDGE_ACCESS_CONST_POS_PERM
                )
                wrap_in_set([edge, rrel_edge, relation_addr], struct_addr)
            elif class_idtf_list is not None and len(class_idtf_list) != 0:
                for class_idtf in class_idtf_list:
                    class_addr = self._keynodes.__getitem__(class_idtf, sc_types.NODE_CONST_CLASS)
                    class_edge = generate_edge(class_addr, part_link_addr, sc_types.EDGE_ACCESS_CONST_POS_PERM)
                    wrap_in_set([class_edge, class_addr], struct_addr)

                edge = generate_edge(tuple_addr, part_link_addr, sc_types.EDGE_ACCESS_CONST_POS_PERM)
                wrap_in_set([edge], struct_addr)

                if self._next_word_link_addr.is_valid():
                    next_edge = generate_edge(self._next_word_link_addr, part_link_addr, sc_types.EDGE_D_COMMON_CONST)
                    rrel_edge = generate_edge(
                        self.nrel_sequence_in_linear_text, next_edge, sc_types.EDGE_ACCESS_CONST_POS_PERM
                    )
                    wrap_in_set([next_edge, rrel_edge], struct_addr)

                self._next_word_link_addr = part_link_addr
                logger.info(f"Generate parts sequence")

            self._visit_parse_tree(part, part_link_addr, struct_addr)

    def _resolve_text_decomposition_tuple(self, text_link_addr: ScAddr, struct_addr: ScAddr) -> ScAddr:
        decomposition_addr = generate_node(sc_types.NODE_CONST_TUPLE)
        common_edge = generate_edge(text_link_addr, decomposition_addr, sc_types.EDGE_D_COMMON_CONST)
        edge = generate_edge(self.nrel_text_decomposition, common_edge, sc_types.EDGE_ACCESS_CONST_POS_PERM)

        wrap_in_set(
            [
                decomposition_addr,
                common_edge,
                edge,
            ],
            struct_addr
        )

        return decomposition_addr

    def _resolve_text(self, words: List[str]) -> ScAddr:
        text = ""
        space = ""
        for word in words:
            if word in self._puncts:
                text += word
            else:
                text += space + word

            space = " "

        logger.info(f"Resolve part text")
        return generate_link(text)

    def _add_word_attributes(self, word_link_addr: ScAddr, class_idtf_list: List[str], struct_addr: ScAddr):
        for class_idtf in class_idtf_list:
            class_addr = self._keynodes.__getitem__(class_idtf, sc_types.NODE_CONST_CLASS)
            class_edge = generate_edge(class_addr, word_link_addr, sc_types.EDGE_ACCESS_CONST_POS_PERM)
            wrap_in_set([class_edge, class_addr], struct_addr)

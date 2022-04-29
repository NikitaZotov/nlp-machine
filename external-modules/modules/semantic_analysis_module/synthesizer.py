"""
    Author Zotov Nikita
"""

from typing import List, Any

from json_client.constants import sc_types
from json_client.dataclass import ScAddr
from json_client.sc_agent import ScKeynodes
from log import get_default_logger
from modules.common.generator import generate_edge, generate_node, wrap_in_set, generate_binary_relation
from modules.semantic_analysis_module.constants import Identifiers

logger = get_default_logger(__name__)


class SemanticSynthesizer:
    def __init__(self):
        self._keynodes = ScKeynodes()
        self.nrel_semantic_structure = self._keynodes.__getitem__(
            Identifiers.NREL_SEMANTIC_STRUCTURE.value, sc_types.NODE_CONST_CLASS
        )

    def synthesize(self, graph: Any, text_link_addr: ScAddr) -> ScAddr:
        logger.info(f"Synthesize syntactic tree")

        struct_addr = generate_node(sc_types.NODE_CONST_STRUCT)
        generate_binary_relation(
            text_link_addr, sc_types.EDGE_D_COMMON_CONST, struct_addr, self.nrel_semantic_structure
        )

        self._visit_graph(graph, struct_addr)
        return struct_addr

    def _visit_graph(self, graph: Any, struct_addr: ScAddr):
        for dep in list(graph.triples()):
            subject_addr = self._keynodes.__getitem__(str(dep[0][0]), sc_types.NODE_CONST)
            relation_addr = self._keynodes.__getitem__("nrel_" + str(dep[1]), sc_types.NODE_CONST_NOROLE)
            object_addr = self._keynodes.__getitem__(str(dep[2][0]), sc_types.NODE_CONST)

            common_edge = generate_edge(subject_addr, object_addr, sc_types.EDGE_D_COMMON_CONST)
            edge = generate_edge(relation_addr, common_edge, sc_types.EDGE_ACCESS_CONST_POS_PERM)

            wrap_in_set([subject_addr, relation_addr, object_addr, common_edge, edge], struct_addr)

    def _resolve_text_decomposition_tuple(self, text_link_addr: ScAddr, struct_addr: ScAddr) -> ScAddr:
        decomposition_addr = generate_node(sc_types.NODE_CONST_TUPLE)
        common_edge = generate_edge(text_link_addr, decomposition_addr, sc_types.EDGE_D_COMMON_CONST)
        edge = generate_edge(self.nrel_semantic_structure, common_edge, sc_types.EDGE_ACCESS_CONST_POS_PERM)

        wrap_in_set(
            [
                decomposition_addr,
                common_edge,
                edge,
            ],
            struct_addr
        )

        return decomposition_addr

    def _add_word_attributes(self, word_link_addr: ScAddr, class_idtf_list: List[str], struct_addr: ScAddr):
        for class_idtf in class_idtf_list:
            class_addr = self._keynodes.__getitem__(class_idtf, sc_types.NODE_CONST_CLASS)
            class_edge = generate_edge(class_addr, word_link_addr, sc_types.EDGE_ACCESS_CONST_POS_PERM)
            wrap_in_set([class_edge, class_addr], struct_addr)

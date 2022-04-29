"""
    Author Zotov Nikita
"""

from typing import Tuple, Dict

from json_client import client
from json_client.constants import sc_types
from json_client.dataclass import ScTemplate, ScAddr
from json_client.sc_agent import ScKeynodes
from log import get_default_logger
from modules.common.constants import ScAlias
from modules.common.generator import generate_edge, generate_node, generate_link, wrap_in_set, generate_binary_relation
from modules.common.identifiers import CommonIdentifiers
from modules.common.searcher import get_edge
from modules.sentence_analysis_module.constants import Identifiers

logger = get_default_logger(__name__)


class SentenceSynthesizer:
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
        self.nrel_lexical_structure = self._keynodes[Identifiers.NREL_LEXICAL_STRUCTURE.value]
        self._lexeme_prefix = 'l_'
        self._puncts = [',', '.', '!', '?', ';', '-', ':']

    def synthesize(self, forms_lexemes: Dict[str, str], text_link_addr: ScAddr) -> ScAddr:
        struct_addr = generate_node(sc_types.NODE_CONST_STRUCT)
        generate_binary_relation(text_link_addr, sc_types.EDGE_D_COMMON_CONST, struct_addr, self.nrel_lexical_structure)

        decomposition_addr = self._generate_text_decomposition_tuple(text_link_addr, struct_addr)

        logger.info("Decompose text")
        self._generate_lexemes_sequence(forms_lexemes, decomposition_addr, struct_addr)

        return struct_addr

    def _find_text_lexical_structure(self, text_link_addr: ScAddr) -> ScAddr:
        template = ScTemplate()
        template.triple_with_relation(
            text_link_addr,
            [sc_types.EDGE_D_COMMON_VAR, ScAlias.COMMON_EDGE.value],
            sc_types.NODE_VAR_TUPLE,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            self.nrel_text_decomposition,
        )
        template.triple(
            [sc_types.NODE_VAR_STRUCT, ScAlias.NODE.value],
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            ScAlias.COMMON_EDGE.value,
        )
        results = client.template_search(template)
        if len(results) != 0:
            return results[0].get(ScAlias.NODE.value)

        return ScAddr(0)

    def _generate_text_decomposition_tuple(self, text_link_addr: ScAddr, struct_addr: ScAddr) -> ScAddr:
        decomposition_addr = generate_node(sc_types.NODE_CONST_TUPLE)
        common_edge = generate_edge(text_link_addr, decomposition_addr, sc_types.EDGE_D_COMMON_CONST)
        edge = generate_edge(self.nrel_text_decomposition, common_edge, sc_types.EDGE_ACCESS_CONST_POS_PERM)

        wrap_in_set(
            [
                text_link_addr,
                decomposition_addr,
                common_edge,
                edge,
                self.nrel_text_decomposition,
                self.nrel_sequence_in_linear_text
            ],
            struct_addr
        )

        return decomposition_addr

    def _generate_lexemes_sequence(
            self, forms_lexemes: Dict[str, str], decomposition_addr: ScAddr, struct_addr: ScAddr
    ) -> None:
        prev_form_addr = ScAddr(0)

        logger.info("Generate lexemes sequence")
        for form, lexeme in forms_lexemes.items():
            if lexeme is None:
                lexeme = form

            if lexeme in self._puncts:
                continue

            _, form_addr = self._resolve_lexeme_and_form(lexeme, form, decomposition_addr, struct_addr)

            if prev_form_addr.is_valid():
                common_edge = generate_edge(prev_form_addr, form_addr, sc_types.EDGE_D_COMMON_CONST)
                edge = generate_edge(
                    self.nrel_sequence_in_linear_text, common_edge, sc_types.EDGE_ACCESS_CONST_POS_PERM
                )
                wrap_in_set([common_edge, edge], struct_addr)
            else:
                template = ScTemplate()
                template.triple(
                    decomposition_addr,
                    [sc_types.EDGE_ACCESS_VAR_POS_PERM, ScAlias.ACCESS_EDGE.value],
                    form_addr,
                )
                results = client.template_search(template)

                if len(results) == 1:
                    edge = generate_edge(
                        self._keynodes[CommonIdentifiers.RREL_ONE.value],
                        results[0].get(ScAlias.ACCESS_EDGE.value),
                        sc_types.EDGE_ACCESS_CONST_POS_PERM)
                    wrap_in_set([edge, self._keynodes[CommonIdentifiers.RREL_ONE.value]], struct_addr)

            prev_form_addr = form_addr

    def _resolve_lexeme_and_form(
            self, lexeme: str, form: str, decomposition_addr: ScAddr, struct_addr: ScAddr
    ) -> Tuple[ScAddr, ScAddr]:
        lexeme_addr = self._keynodes.__getitem__(self._lexeme_prefix + lexeme, sc_types.NODE_CONST)

        class_edge = get_edge(self.concept_lexeme, lexeme_addr, sc_types.EDGE_ACCESS_VAR_POS_PERM)
        if not class_edge.is_valid():
            class_edge = generate_edge(self.concept_lexeme, lexeme_addr, sc_types.EDGE_ACCESS_CONST_POS_PERM)

        form_addr, link_edge = self._resolve_lexeme_form(lexeme_addr, form)

        edge = get_edge(decomposition_addr, form_addr, sc_types.EDGE_ACCESS_VAR_POS_PERM)
        if not edge.is_valid():
            edge = generate_edge(decomposition_addr, form_addr, sc_types.EDGE_ACCESS_CONST_POS_PERM)

        wrap_in_set([lexeme_addr, class_edge, edge, form_addr, link_edge], struct_addr)

        return lexeme_addr, form_addr

    def _resolve_lexeme_form(self, lexeme_addr: ScAddr, lexeme: str) -> Tuple[ScAddr, ScAddr]:
        form_addr = generate_link(lexeme)
        edge = generate_edge(lexeme_addr, form_addr, sc_types.EDGE_ACCESS_CONST_POS_PERM)

        return form_addr, edge

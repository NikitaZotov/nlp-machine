"""
    Author Zotov Nikita
"""

from typing import List

from json_client.constants import sc_types
from json_client.dataclass import ScAddr
from json_client.sc_agent import ScKeynodes
from log import get_default_logger
from modules.common.generator import generate_edge, generate_node, generate_binary_relation
from modules.common.searcher import check_edge, get_element_by_norole_relation
from modules.lexical_analysis_module.constants import Identifiers

logger = get_default_logger(__name__)


class LexemeSynthesizer:
    def __init__(self):
        self._keynodes = ScKeynodes()
        self.nrel_paradigm = self._keynodes.__getitem__(
            Identifiers.NREL_PARAGIGM.value, sc_types.NODE_CONST_NOROLE
        )
        self.rrel_singular = self._keynodes.__getitem__(Identifiers.RREL_SINGULAR.value, sc_types.NODE_CONST_ROLE)
        self.rrel_plural = self._keynodes.__getitem__(Identifiers.RREL_PLURAL.value, sc_types.NODE_CONST_ROLE)
        self._lexeme_prefix = 'l_'

    def synthesize(
            self, lexeme: str, lexeme_signs: List[str], base_form: str, base_form_signs: List[str], is_plural: bool
    ) -> None:
        has_paradigm = True
        if base_form is None:
            base_form = lexeme
            has_paradigm = False

        base_form_addr = self._keynodes.__getitem__(self._lexeme_prefix + base_form, sc_types.NODE_CONST)

        for sign in base_form_signs:
            sign_addr = self._keynodes.__getitem__(sign, sc_types.NODE_CONST_CLASS)

            if not check_edge(sign_addr, base_form_addr, sc_types.EDGE_ACCESS_VAR_POS_PERM):
                generate_edge(sign_addr, base_form_addr, sc_types.EDGE_ACCESS_CONST_POS_PERM)

        if has_paradigm:
            logger.info("Resolve lexeme paradigm")
            paradigm = self._resolve_lexeme_paradigm(base_form_addr)
            logger.info("Synthesize lexeme form")
            self._synthesize_lexeme_form(paradigm, lexeme, lexeme_signs, is_plural)

    def _resolve_lexeme_paradigm(self, base_form_addr: ScAddr) -> ScAddr:
        paradigm = get_element_by_norole_relation(base_form_addr, self.nrel_paradigm)
        if paradigm is None or not paradigm.is_valid():
            paradigm = generate_node(sc_types.NODE_CONST)
            generate_binary_relation(base_form_addr, sc_types.EDGE_D_COMMON_CONST, paradigm, self.nrel_paradigm)

        return paradigm

    def _synthesize_lexeme_form(self, paradigm: ScAddr, lexeme: str, lexeme_signs: List[str], is_plural: bool) -> None:
        if is_plural:
            relation = self.rrel_plural
        else:
            relation = self.rrel_singular

        lexeme_addr = self._keynodes.__getitem__(lexeme, sc_types.NODE_CONST_CLASS)
        for sign in lexeme_signs:
            sign_addr = self._keynodes.__getitem__(sign, sc_types.NODE_CONST_CLASS)

            if not check_edge(sign_addr, lexeme_addr, sc_types.EDGE_ACCESS_VAR_POS_PERM):
                generate_edge(sign_addr, lexeme_addr, sc_types.EDGE_ACCESS_CONST_POS_PERM)

        if not check_edge(paradigm, lexeme_addr, sc_types.EDGE_ACCESS_VAR_POS_PERM):
            generate_binary_relation(paradigm, sc_types.EDGE_ACCESS_CONST_POS_PERM, lexeme_addr, relation)

"""
    Author Zotov Nikita
"""
from typing import Dict, List

from json_client import client
from json_client.constants import sc_types
from json_client.dataclass import ScTemplate, ScAddr
from json_client.sc_keynodes import ScKeynodes
from modules.common.constants import ScAlias
from modules.common.generator import \
    (
        generate_link,
        generate_edge,
        set_en_main_idtf,
        generate_node,
        generate_binary_relation,
    )
from modules.common.identifiers import ActionIdentifiers, QuestionStatus, CommonIdentifiers
from modules.common.searcher import get_element_by_norole_relation, get_system_idtf, get_element_by_role_relation, \
    get_element_by_main_idtf
from modules.common.utils import complete_agent
from .constants import Identifiers, Keywords
from .lexeme_translator import LexemeTranslator


class NLPService:
    def __init__(self):
        self._keynodes = ScKeynodes()
        self._translator = LexemeTranslator()

    def analyse_text_lexemes(self, text: str, text_article: str) -> bool:
        text_link_addr = generate_link(text)

        text_addr = generate_node(sc_types.NODE_CONST)
        generate_edge(self._keynodes[Identifiers.CONCEPT_TEXT.value], text_addr, sc_types.EDGE_ACCESS_CONST_POS_PERM)
        set_en_main_idtf(text_addr, text_article)

        text_tuple_addr = generate_node(sc_types.NODE_CONST_TUPLE)
        generate_binary_relation(
            text_tuple_addr,
            sc_types.EDGE_D_COMMON_CONST,
            text_addr,
            self._keynodes.__getitem__(CommonIdentifiers.NREL_SC_TEXT_TRANSLATION.value, sc_types.NODE_CONST_NOROLE)
        )
        generate_edge(text_tuple_addr, text_link_addr, sc_types.EDGE_ACCESS_CONST_POS_PERM)

        generate_edge(
            self._keynodes[CommonIdentifiers.LANG_EN.value], text_link_addr, sc_types.EDGE_ACCESS_CONST_POS_PERM
        )

        _, result = complete_agent(
            {text_link_addr: False},
            [ActionIdentifiers.ACTION_LEXICAL_GRAMMAR_ANALYSIS_AGENT.value, CommonIdentifiers.QUESTION.value],
            reaction=QuestionStatus.QUESTION_FINISHED_SUCCESSFULLY,
            wait_time=10
        )

        return result

    def resolve_lexemes(self, text_article: str) -> Dict[str, Dict[str, str]]:
        text_link_addr = self._get_text_link_by_article(text_article)

        if text_link_addr is None or not text_link_addr.is_valid():
            return {}

        decomposition_addr = self._get_text_decomposition(text_link_addr)
        if not decomposition_addr.is_valid():
            return {}

        elements = self._get_linear_text_forms(decomposition_addr)

        lexemes_dict = {}
        for element in elements:
            lexeme_addr = self._translator.resolve_form_lexeme(element)

            if not lexeme_addr.is_valid():
                continue

            lexeme = get_system_idtf(lexeme_addr)[2::1]
            paradigm = self._translator.resolve_lexeme_paradigm(lexeme_addr)
            attributes = self._translator.resolve_lexeme_attributes(lexeme_addr)

            lexemes_dict.update(
                {lexeme: {Keywords.PARADIGM.value: paradigm, Keywords.ATTRIBUTES.value: attributes}}
            )

        return lexemes_dict

    def _get_text_decomposition(self, text_link_addr: ScAddr) -> ScAddr:
        template = ScTemplate()
        template.triple_with_relation(
            text_link_addr,
            [sc_types.EDGE_D_COMMON_VAR, ScAlias.COMMON_EDGE.value],
            [sc_types.NODE_VAR_TUPLE, ScAlias.NODE.value],
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            self._keynodes[Identifiers.NREL_TEXT_DECOMPOSITION.value],
        )
        results = client.template_search(template)

        if len(results) != 0:
            return results[0].get(ScAlias.NODE.value)

        return ScAddr(0)

    def _get_text_link_by_article(self, text_article: str) -> ScAddr:
        if len(text_article) == 0:
            return ScAddr(0)

        text_addr = get_element_by_main_idtf(text_article)
        if not text_addr.is_valid():
            return text_addr

        template = ScTemplate()
        template.triple_with_relation(
            [sc_types.NODE_VAR_TUPLE, ScAlias.ELEMENT.value],
            [sc_types.EDGE_D_COMMON_VAR, ScAlias.COMMON_EDGE.value],
            text_addr,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            self._keynodes[CommonIdentifiers.NREL_SC_TEXT_TRANSLATION.value],
        )
        template.triple(
            ScAlias.ELEMENT.value,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            [sc_types.LINK_VAR, ScAlias.LINK.value]
        )
        result = client.template_search(template)
        if not len(result) == 0:
            return result[0].get(ScAlias.LINK.value)

        return ScAddr(0)

    def get_text_by_article(self, text_article: str) -> str:
        link = self._get_text_link_by_article(text_article)

        if link.is_valid():
            return client.get_link_content(link).data

        return ""

    def get_text_lexical_structure(self, text_article: str) -> ScAddr:
        text_link_addr = self._get_text_link_by_article(text_article)

        template = ScTemplate()
        template.triple(
            [sc_types.NODE_VAR_STRUCT, ScAlias.NODE.value],
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            text_link_addr
        )
        result = client.template_search(template)

        if len(result) == 0:
            return ScAddr(0)

        return result[0].get(ScAlias.NODE.value)

    def _get_linear_text_forms(self, decomposition_addr: ScAddr) -> List[ScAddr]:
        link = get_element_by_role_relation(decomposition_addr, self._keynodes[CommonIdentifiers.RREL_ONE.value])

        links = []
        while link is not None and link.is_valid():
            links.append(link)

            next_link = get_element_by_norole_relation(
                link, self._keynodes[Identifiers.NREL_SEQUENCE_IN_LINEAR_TEXT.value]
            )
            link = next_link

        return links

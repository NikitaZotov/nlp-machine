"""
    Author Zotov Nikita
"""
from typing import Dict, List, Tuple

from json_client import client
from json_client.constants import sc_types
from json_client.dataclass import ScTemplate, ScAddr
from json_client.sc_keynodes import ScKeynodes
from modules.common.constants import ScAlias
from modules.common.generator import generate_link, generate_edge
from modules.common.identifiers import ActionIdentifiers, QuestionStatus, CommonIdentifiers
from modules.common.searcher import get_element_by_norole_relation, get_system_idtf, get_element_by_role_relation
from modules.common.utils import complete_agent
from modules.sentence_analysis_module.generator import set_system_idtf
from .constants import Identifiers


class AgentsService:
    def __init__(self):
        self._keynodes = ScKeynodes()

    def analyse_text_lexemes(self, text: str, text_article: str) -> bool:
        text_link_addr = generate_link(text)
        set_system_idtf(text_link_addr, text_article)
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

    def resolve_lexemes(self, text_article: str) -> Dict[str, Tuple[Dict[str, Dict[str, str]], Dict[str, List[str]]]]:
        text_link_addr = self._keynodes[text_article]

        if text_link_addr is None or not text_link_addr.is_valid():
            return {}

        nrel_text_decomposition = self._keynodes[Identifiers.NREL_TEXT_DECOMPOSITION.value]

        template = ScTemplate()
        template.triple_with_relation(
            text_link_addr,
            [sc_types.EDGE_D_COMMON_VAR, ScAlias.COMMON_EDGE.value],
            [sc_types.NODE_VAR_TUPLE, ScAlias.NODE.value],
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            nrel_text_decomposition,
        )
        results = client.template_search(template)

        decomposition_tuple = None
        if len(results) != 0:
            decomposition_tuple = results[0].get(ScAlias.NODE.value)
        else:
            return {}

        elements = self._get_linear_text_elements(decomposition_tuple)

        lexemes_dict = {}
        for element in elements:
            lexeme_addr = self._resolve_lexeme(element)

            if lexeme_addr.is_valid():
                lexeme = get_system_idtf(lexeme_addr)[2::1]
                paradigm_dict = self._resolve_lexeme_paradigm(lexeme_addr)
                signs_dict = self._resolve_lexeme_signs(lexeme_addr)

                lexemes_dict.update({lexeme: (paradigm_dict, signs_dict)})

        return lexemes_dict

    def get_text_by_article(self, text_article: str) -> str:
        if len(text_article) == 0:
            return ""
        text_link_addr = self._keynodes[text_article]
        if text_link_addr is not None and text_link_addr.is_valid():
            return client.get_link_content(text_link_addr).data

        return ""

    def _resolve_lexeme(self, text_link_element: ScAddr) -> ScAddr:
        template = ScTemplate()
        template.triple(
            [sc_types.NODE_VAR, ScAlias.NODE.value],
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            text_link_element,
        )
        template.triple(
            self._keynodes[Identifiers.CONCEPT_LEXEME.value],
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            ScAlias.NODE.value,
        )
        results = client.template_search(template)

        if len(results) != 0:
            return results[0].get(ScAlias.NODE.value)

        return ScAddr(0)

    def _resolve_lexeme_paradigm(self, lexeme_addr: ScAddr) -> Dict[str, Dict[str, str]]:
        paradigm_addr = get_element_by_norole_relation(lexeme_addr, self._keynodes[Identifiers.NREL_PARAGIGM.value])

        paradigm_dict = {}
        if paradigm_addr is not None and paradigm_addr.is_valid():
            numbers_dict = {}

            numbers_dict.update(self._resolve_singular_forms(paradigm_addr))
            numbers_dict.update(self._resolve_plural_forms(paradigm_addr))

            paradigm_dict.update({'paradigm': numbers_dict})

        return paradigm_dict

    def _resolve_singular_forms(self, paradigm_addr: ScAddr) -> Dict[str, str]:
        singular_form_addr = get_element_by_role_relation(
            paradigm_addr, self._keynodes[Identifiers.RREL_SINGULAR.value]
        )
        if singular_form_addr is not None and singular_form_addr.is_valid():
            return {'singular': get_system_idtf(singular_form_addr)}

        return {}

    def _resolve_plural_forms(self, paradigm_addr: ScAddr) -> Dict[str, str]:
        plural_form_addr = get_element_by_role_relation(
            paradigm_addr, self._keynodes[Identifiers.RREL_PLURAL.value]
        )
        if plural_form_addr is not None and plural_form_addr.is_valid():
            return {'plural': get_system_idtf(plural_form_addr)}

        return {}

    def _get_linear_text_elements(self, decomposition_addr: ScAddr) -> List[ScAddr]:
        link = get_element_by_role_relation(decomposition_addr, self._keynodes[CommonIdentifiers.RREL_ONE.value])

        links = []
        while link is not None and link.is_valid():
            links.append(link)

            next_link = get_element_by_norole_relation(
                link, self._keynodes[Identifiers.NREL_SEQUENCE_IN_LINEAR_TEXT.value]
            )
            link = next_link

        return links

    def _resolve_lexeme_signs(self, lexeme_addr: ScAddr) -> Dict[str, str]:
        template = ScTemplate()
        template.triple(
            [sc_types.NODE_VAR_CLASS, ScAlias.NODE.value],
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            lexeme_addr,
        )
        results = client.template_search(template)

        signs: str = ""
        signs_list = []
        for result in results:
            class_addr = result.get(ScAlias.NODE.value)

            link = self._get_en_main_idtf_link(class_addr)
            if not link.is_valid():
                continue

            link_content = client.get_link_content(link).data
            if link_content in signs_list:
                continue

            if len(signs) == 0:
                signs += link_content
            else:
                signs += ", " + link_content

            signs_list.append(link_content)

        return {"signs": signs}

    def _get_en_main_idtf_link(self, addr: ScAddr) -> ScAddr:
        template = ScTemplate()
        template.triple_with_relation(
            addr,
            sc_types.EDGE_D_COMMON_VAR,
            [sc_types.LINK_VAR, ScAlias.LINK.value],
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            self._keynodes[CommonIdentifiers.NREL_MAIN_IDENTIFIER.value]
        )
        template.triple(
            self._keynodes[CommonIdentifiers.LANG_EN.value],
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            ScAlias.LINK.value,
        )
        idtf_results = client.template_search(template)

        if len(idtf_results) != 0:
            return idtf_results[0].get(ScAlias.LINK.value)

        return ScAddr(0)

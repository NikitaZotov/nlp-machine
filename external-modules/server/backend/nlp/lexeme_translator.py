"""
    Author Zotov Nikita
"""
from typing import Dict, List

from json_client import client
from json_client.constants import sc_types
from json_client.dataclass import ScTemplate, ScAddr
from json_client.sc_keynodes import ScKeynodes
from modules.common.constants import ScAlias
from modules.common.searcher import \
    (
        get_element_by_norole_relation,
        get_element_by_role_relation,
        get_en_main_idtf_link,
        get_system_idtf
    )
from server.backend.nlp.constants import Identifiers, Keywords


class LexemeTranslator:
    def __init__(self):
        self._keynodes = ScKeynodes()

    def resolve_form_lexeme(self, form_addr: ScAddr) -> ScAddr:
        template = ScTemplate()
        template.triple(
            [sc_types.NODE_VAR, ScAlias.NODE.value],
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            form_addr,
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

    def resolve_lexeme_paradigm(self, lexeme_addr: ScAddr) -> Dict[str, str]:
        paradigm_addr = get_element_by_norole_relation(lexeme_addr, self._keynodes[Identifiers.NREL_PARAGIGM.value])

        if paradigm_addr is None or not paradigm_addr.is_valid():
            return {}

        numbers_dict = {}

        singular_forms = self._resolve_singular_forms(paradigm_addr)
        if not len(singular_forms) == 0:
            numbers_dict.update({Keywords.SINGULAR.value: singular_forms[0]})

        plural_forms = self._resolve_plural_forms(paradigm_addr)
        if not len(plural_forms) == 0:
            numbers_dict.update({Keywords.PLURAL.value: plural_forms[0]})

        return numbers_dict

    def _resolve_singular_forms(self, paradigm_addr: ScAddr) -> List[str]:
        singular_form_addr = get_element_by_role_relation(
            paradigm_addr, self._keynodes[Identifiers.RREL_SINGULAR.value]
        )
        if singular_form_addr is not None and singular_form_addr.is_valid():
            idtf = get_system_idtf(singular_form_addr)
            if idtf:
                return [idtf]

        return []

    def _resolve_plural_forms(self, paradigm_addr: ScAddr) -> List[str]:
        plural_form_addr = get_element_by_role_relation(
            paradigm_addr, self._keynodes[Identifiers.RREL_PLURAL.value]
        )
        if plural_form_addr is not None and plural_form_addr.is_valid():
            idtf = get_system_idtf(plural_form_addr)
            if idtf:
                return [idtf]

        return []

    def resolve_lexeme_attributes(self, lexeme_addr: ScAddr) -> str:
        template = ScTemplate()
        template.triple(
            [sc_types.NODE_VAR_CLASS, ScAlias.NODE.value],
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            lexeme_addr,
        )
        results = client.template_search(template)

        attributes: str = ""
        attributes_list = []
        for result in results:
            class_addr = result.get(ScAlias.NODE.value)

            link = get_en_main_idtf_link(class_addr)
            if not link.is_valid():
                continue

            link_content = client.get_link_content(link).data
            if link_content in attributes_list:
                continue

            if len(attributes) == 0:
                attributes += link_content
            else:
                attributes += ", " + link_content

            attributes_list.append(link_content)

        return attributes

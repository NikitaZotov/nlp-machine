"""
    Author Zotov Nikita
"""

from json_client.constants import sc_types
from json_client.dataclass import ScAddr
from json_client.sc_keynodes import ScKeynodes
from modules.common.generator import generate_link, generate_binary_relation, generate_edge
from modules.common.identifiers import CommonIdentifiers


def set_main_idtf(addr: ScAddr, name):
    keynodes = ScKeynodes()
    lang_ru, nrel_main_idtf = keynodes[CommonIdentifiers.LANG_RU, CommonIdentifiers.NREL_MAIN_IDENTIFIER.value]

    link = generate_link(name)
    generate_edge(lang_ru, name, sc_types.EDGE_ACCESS_VAR_POS_PERM)
    generate_binary_relation(addr, sc_types.EDGE_D_COMMON_CONST, link, nrel_main_idtf)

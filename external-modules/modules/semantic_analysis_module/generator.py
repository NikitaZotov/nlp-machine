"""
    Author Zotov Nikita
"""

from json_client.constants import sc_types
from json_client.dataclass import ScAddr
from json_client.sc_keynodes import ScKeynodes
from modules.common.generator import generate_link, generate_binary_relation, generate_edge
from modules.common.identifiers import CommonIdentifiers


def set_system_idtf(addr: ScAddr, name: str):
    keynodes = ScKeynodes()
    lang_en = keynodes[CommonIdentifiers.LANG_EN.value]
    nrel_sys_idtf = keynodes[CommonIdentifiers.NREL_SYSTEM_IDENTIFIER.value]

    link = generate_link(name)
    generate_edge(lang_en, link, sc_types.EDGE_ACCESS_CONST_POS_PERM)
    generate_binary_relation(addr, sc_types.EDGE_D_COMMON_CONST, link, nrel_sys_idtf)

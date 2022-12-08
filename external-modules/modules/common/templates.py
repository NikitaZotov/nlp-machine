"""
    Author Zotov Nikita
"""

from json_client.constants import sc_types
from json_client.dataclass import ScAddr, ScTemplate
from modules.common.constants import ScAlias


def template_next_element_of_oriented_set(set_node: ScAddr, curr_element_edge: ScAddr, relation: ScAddr) -> ScTemplate:
    templ = ScTemplate()
    templ.triple_with_relation(
        curr_element_edge,
        sc_types.EDGE_D_COMMON_VAR,
        [sc_types.EDGE_ACCESS_VAR_POS_PERM, ScAlias.ACCESS_EDGE.value],
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        relation,
    )
    templ.triple(set_node, ScAlias.ACCESS_EDGE.value, [sc_types.UNKNOWN, ScAlias.ELEMENT.value])
    return templ

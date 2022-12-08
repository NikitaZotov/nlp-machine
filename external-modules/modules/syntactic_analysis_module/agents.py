"""
    Author Zotov Nikita
"""

from log import get_default_logger

from json_client.constants import common, sc_types
from json_client.dataclass import ScAddr, ScEvent
from json_client.sc_agent import ScAgent
from modules.common.exception import CustomException
from modules.common.generator import generate_event, generate_binary_relation, generate_node, generate_edge
from modules.common.identifiers import ActionIdentifiers, CommonIdentifiers, QuestionStatus
from modules.common.log_messages import (
    generate_finish_message,
    generate_start_message,
)
from modules.common.searcher import get_element_by_role_relation
from modules.common.utils import finish_action_status, validate_action
from modules.syntactic_analysis_module.analyser import SyntacticAnalyser

logger = get_default_logger(__name__)


class SyntacticAnalysisAgent(ScAgent):
    action = ActionIdentifiers.ACTION_SYNTACTIC_ANALYSIS_AGENT.value

    def register(self) -> ScEvent:
        return generate_event(
            SyntacticAnalysisAgent.keynodes[QuestionStatus.QUESTION_INITIATED.value],
            common.ScEventType.ADD_OUTGOING_EDGE,
            SyntacticAnalysisAgent.run_impl,
        )

    @staticmethod
    def run_impl(action_class: ScAddr, edge: ScAddr, action_node: ScAddr) -> None:  # pylint: disable=W0613
        if validate_action(SyntacticAnalysisAgent.action, action_node):
            logger.info(generate_start_message(SyntacticAnalysisAgent))
            keynodes = SyntacticAnalysisAgent.keynodes
            try:
                text_link_addr = get_element_by_role_relation(action_node, keynodes[CommonIdentifiers.RREL_ONE.value])

                an = SyntacticAnalyser()
                struct_addr = an.analyse(text_link_addr)

                answer_addr = generate_node(sc_types.NODE_CONST)
                generate_edge(answer_addr, struct_addr, sc_types.EDGE_ACCESS_CONST_POS_PERM)
                generate_binary_relation(
                    action_node,
                    sc_types.EDGE_D_COMMON_CONST,
                    answer_addr,
                    keynodes[CommonIdentifiers.NREL_ANSWER.value]
                )

                finish_action_status(action_node)
            except CustomException as ex:
                finish_action_status(action_node, False)
                logger.error(str(ex))
            logger.info(generate_finish_message(SyntacticAnalysisAgent))

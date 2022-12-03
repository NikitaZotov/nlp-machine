"""
    Author Zotov Nikita
"""

from enum import Enum


class ActionIdentifiers(Enum):
    ACTION_LEXICAL_ANALYSIS_AGENT = "action_lexical_analysis_agent"
    ACTION_LEXICAL_GRAMMAR_ANALYSIS_AGENT = "action_lexical_grammar_analysis_agent"
    ACTION_SENTENCES_ANALYSIS_AGENT = "action_sentences_analysis_agent"
    ACTION_SYNTACTIC_ANALYSIS_AGENT = "action_syntactic_analysis_agent"
    ACTION_SEMANTIC_ANALYSIS_AGENT = "action_semantic_analysis_agent"


class CommonIdentifiers(Enum):
    QUESTION = "question"
    RREL_DYNAMIC_ARGUMENT = "rrel_dynamic_argument"
    RREL_ONE = "rrel_1"
    RREL_TWO = "rrel_2"
    NREL_BASIC_SEQUENCE = "nrel_basic_sequence"
    NREL_SC_TEXT_TRANSLATION = "nrel_sc_text_translation"
    NREL_SYSTEM_IDENTIFIER = "nrel_system_identifier"
    NREL_MAIN_IDENTIFIER = "nrel_main_idtf"
    NREL_ANSWER = "nrel_answer"
    LANG_RU = "lang_ru"
    LANG_EN = "lang_en"


class QuestionStatus(Enum):
    QUESTION_INITIATED = "question_initiated"
    QUESTION_FINISHED = "question_finished"
    QUESTION_FINISHED_SUCCESSFULLY = "question_finished_successfully"
    QUESTION_FINISHED_UNSUCCESSFULLY = "question_finished_unsuccessfully"

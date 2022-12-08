"""
    Author Zotov Nikita
"""

from enum import Enum


class Identifiers(Enum):
    NREL_PARAGIGM = "nrel_paradigm"
    RREL_SINGULAR = "rrel_singular"
    RREL_PLURAL = "rrel_plural"
    CONCEPT_LEXEME = "concept_lexeme"
    NREL_TEXT_DECOMPOSITION = "nrel_text_decomposition"
    NREL_SEQUENCE_IN_LINEAR_TEXT = "nrel_sequence_in_linear_text"
    NREL_LEXICAL_STRUCTURE = "nrel_lexical_structure"
    NREL_SYNTACTIC_STRUCTURE = "nrel_syntactic_structure"
    NREL_SEMANTIC_STRUCTURE = "nrel_semantic_structure"
    CONCEPT_TEXT = "concept_text"


class Keywords(Enum):
    PARADIGM = "paradigm"
    SINGULAR = "singular"
    PLURAL = "plural"
    ATTRIBUTES = "attributes"

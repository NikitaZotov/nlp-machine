"""
    Author Zotov Nikita
"""

from typing import Tuple, List, Dict
import inflect

import nltk
from nltk.stem import WordNetLemmatizer

from json_client import client
from json_client.dataclass import ScAddr
from log import get_default_logger
from modules.lexical_analysis_module.synthesizer import LexemeSynthesizer
from modules.lexical_analysis_module.speech_parts import speech_parts

logger = get_default_logger(__name__)


class LexicalAnalyser:
    def __init__(self):
        self._tokens = None
        self._tags = None
        self._abrs = ['NN', 'VB', 'JJ']

        self._lemmatizer = WordNetLemmatizer()
        self._synthesizer = LexemeSynthesizer()
        self._inflect = inflect.engine()

    def analyse(self, text_link_addr: ScAddr) -> Dict[str, str]:
        text = client.get_link_content(text_link_addr).data

        self.tag_text_words(text)
        logger.info("Tag text words")

        forms_lexemes = {}
        for tagged in self._tags:
            lexeme, pos = tagged

            signs = speech_parts.get(pos)
            if signs is not None:
                base_form, is_plural = self.lemmatize_lexeme(lexeme, pos)
                logger.info("Lemmatize lexeme \"" + lexeme + "\"")

                if base_form is not None:
                    _, base_form_tag = nltk.pos_tag([base_form])[0]
                    base_form_signs = speech_parts.get(base_form_tag)
                else:
                    base_form_signs = signs

                self._synthesizer.synthesize(lexeme, signs, base_form, base_form_signs, is_plural)
                logger.info("Synthesize lexeme")

                forms_lexemes.update({lexeme: base_form})

        return forms_lexemes

    def tag_text_words(self, text) -> List[Tuple[str, str]]:
        self._tokens = nltk.word_tokenize(text)
        self._tags = nltk.pos_tag(self._tokens)

        return self._tags

    def lemmatize_lexeme(self, lexeme: str, pos: str) -> Tuple[str, bool]:
        is_plural = False
        base_form = None

        if pos.startswith('NN'):
            base_form = self._lemmatizer.lemmatize(lexeme, 'n')
            if self._inflect.plural_noun(lexeme) == lexeme:
                is_plural = True

        elif pos.startswith('VB'):
            base_form = self._lemmatizer.lemmatize(lexeme, 'v')
            if self._inflect.plural_verb(lexeme) == lexeme:
                is_plural = True

        elif pos.startswith('JJ'):
            base_form = self._lemmatizer.lemmatize(lexeme, 'a')
            if self._inflect.plural_adj(lexeme) == lexeme:
                is_plural = True

        return base_form, is_plural

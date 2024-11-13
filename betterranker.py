# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long

import math

from .corpus import Corpus
from .invertedindex import InvertedIndex
from .posting import Posting
from .ranker import Ranker


class BetterRanker(Ranker):
    """
    A ranker that does traditional TF-IDF ranking, possibly combining it with
    a static document score (if present).

    The static document score is assumed accessible in a document field named
    "static_quality_score". If the field is missing or doesn't have a value, a
    default value of 0.0 is assumed for the static document score.

    See Section 7.1.4 in https://nlp.stanford.edu/IR-book/pdf/irbookonlinereading.pdf.
    """

    # These values could be made configurable. Hardcode them for now.
    _dynamic_score_weight = 1.0
    _static_score_weight = 1.0
    _static_score_field_name = "static_quality_score"
    _static_score_default_value = 0.0

    def __init__(self, corpus: Corpus, inverted_index: InvertedIndex):
        self._score = 0.0
        self._document_id = None
        self._corpus = corpus
        self._inverted_index = inverted_index

    def reset(self, document_id: int) -> None:
        self._score = 0.0
        self._document_id = document_id

    def update(self, term: str, multiplicity: int, posting: Posting) -> None:
        assert self._document_id == posting.document_id

        tf = posting.term_frequency * multiplicity
        tf_adjusted = tf + 1

        df = self._inverted_index.get_document_frequency(term)
        df_adjusted = df or 1
        ## NOTE: ^ Blir dette riktig å gjøre ? altså for å ikke dele på 0, men og bevare "næyaktigheten"
        idf = math.log10(self._corpus.size() / df_adjusted)

        score = math.log(tf_adjusted) * idf
        self._score += score

    def evaluate(self) -> float:
        assert self._document_id is not None

        static_score = self._corpus[self._document_id].get_field(
            self._static_score_field_name, self._static_score_default_value
        )

        total_score = (
            self._score * self._dynamic_score_weight
            + static_score * self._static_score_weight
        )
        return total_score

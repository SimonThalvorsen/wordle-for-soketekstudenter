from typing import List

from in3120 import Vectorizer, InvertedIndex, Corpus

# pylint: disable=missing-module-docstring
# pylint: disable=unnecessary-pass

from abc import ABC, abstractmethod
from .posting import Posting

class Ranker(ABC):
    """
    Abstract base class for rankers used together with document-at-a-time traversal.
    """

    @abstractmethod
    def reset(self, document_id: int) -> None:
        """
        Resets the ranker, i.e., prepares it for evaluating another document.
        """
        pass

    @abstractmethod
    def update(self, term: str, multiplicity: int, posting: Posting) -> None:
        """
        Tells the ranker to update its internals based on information from one
        query term and the associated posting. This method might be invoked multiple
        times if the query contains multiple unique terms. Since a query term might
        occur multiple times in a query, the query term's multiplicity or occurrence
        count in the query is also provided.
        """
        pass

    @abstractmethod
    def evaluate(self) -> float:
        """
        Returns the current document's relevancy score. I.e., evaluates how relevant
        the current document is, given all the previous update invocations.
        """
        pass


class WordleRanker(Ranker):
    """
    A ranker optimized for Wordle by scoring based on letter frequency and positional feedback.
    """
    def __init__(self, corpus: Corpus, inverted_index: InvertedIndex, vectorizer: Vectorizer):
        self._score = 0.0
        self._document_id = None
        self._corpus = corpus
        self._inverted_index = inverted_index
        self._vectorizer = vectorizer

    def reset(self, document_id: int) -> None:
        self._score = 0.0
        self._document_id = document_id

    def update(self, term: str, multiplicity: int, posting: Posting) -> None:
        assert self._document_id is not None
        doc_id = None
        ## NOTE: This is not optimal, but how it has to be done due to the limitations of the files
        for doc in self._corpus:
            if doc.get_field("body", "") == term:
                doc_id = doc.document_id
                break
        assert doc_id is not None
        if doc_id == posting.document_id: return # Same word, no need to guess twice, big optimization am I right? ;)

        guess_vector = self._vectorizer.from_document(self._corpus.get_document(doc_id), fields=["body"])
        target_vector = self._vectorizer.from_document(self._corpus.get_document(posting.document_id), fields=["body"])
        self._score += guess_vector.cosine(target_vector)

    def evaluate(self) -> float:
        assert self._document_id is not None
        return self._score

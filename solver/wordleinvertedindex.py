from bisect import insort
from collections import Counter, defaultdict

from context import in3120


class WordleInvertedIndex:

    def __init__(self, corpus: in3120.Corpus):
        self.corpus = corpus
        self.posting_lists = defaultdict(list)
        self.build_index()

    def build_index(self) -> None:
        for i, document in enumerate(self.corpus):
            w = document.get_field("body", "")
            term_freq = Counter(w)

            for pos, c in enumerate(w):
                self._append_to_posting_list(c, pos, i, term_freq[c])

    def _append_to_posting_list(
        self, letter: str, pos: int, word_id: int, tf: int
    ) -> None:
        posting_list = self.posting_lists[(letter, pos)]
        insort(posting_list, in3120.Posting(word_id, tf), key=lambda x: x.document_id)

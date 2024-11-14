from bisect import insort
from collections import Counter, defaultdict
from context import in3120

class MyInvertedIndex() :

    def __init__(self, corpus):
        self._corpus = corpus
        self._posting_lists = defaultdict(list)
        self._build_index()

    def _build_index(self) -> None:
        for i, w in enumerate(self._corpus):
            term_freq = Counter(w)
    
            for pos, c in enumerate(w) :
                self._append_to_posting_list(c, pos, i, term_freq[c])

    def _append_to_posting_list(self, letter: str, pos: int, word_id:int, tf:int) -> None:
        posting_list = self._posting_lists[(letter, pos)]
        insort(posting_list, in3120.Posting(word_id, tf), key= lambda x : x.document_id)


from collections import Counter
from typing import Dict, List, Set, Tuple
from wordleinvertedindex import MyInvertedIndex
from context import in3120

class SolverSearchEngine :

    def __init__(self, corpus: in3120.Corpus) -> None:
        """
        class that, from a feedback and the guessed word, returns a list of indices of all the possible words using get_possible_matches()
        """
        self._inverted_index = MyInvertedIndex(corpus)

    def _green(self, unwanted_terms: Set, position: int, char: str) -> Set[Tuple[str,int]]:
        #returns all the words having a different letter at this position
        for term, pos in self._inverted_index._posting_lists.keys():
            if pos == position and term != char :
                unwanted_terms.add((term, pos))

    def _yellow(self, unwanted_terms: Set, position: int, char: str) -> Set[Tuple[str,int]] :
        #returns all the words having the same letter at this position
        unwanted_terms.add((char, position))
        
    def _gray(self, unwanted_terms: Set, char: str) -> Set[Tuple[str,int]]:
        #returns all the words having this letter
        for term, pos in self._inverted_index._posting_lists.keys():
            if term == char :
                unwanted_terms.add((term, pos))

    def _remove_duplicates(self, char, count) :
        t = set()
        self._gray(t, char)
        for (term, pos) in t :
            posting_list = self._inverted_index._posting_lists[(term, pos)]
            self._inverted_index._posting_lists[(term, pos)] = [posting for posting in posting_list if posting.term_frequency <= count]

    def _update_index(self, feedback, guess) -> Dict[Tuple[str,int],List[in3120.Posting]]:
        # Example feedback format: [('a', '1'), ('b', '1'), ('a', '2'), ('c', '2'), ('k', '2')]
        unwanted_terms = set()
        counter = {c:0 for c in guess}

        for i, (c, score) in enumerate(feedback) :
            if score == '2' :
                # c is correct
                self._green(unwanted_terms, i, c)
                counter[c] +=1
            elif score == '1' :
                # c is in the wrong pos 
                self._yellow(unwanted_terms, i,c)
                counter[c] +=1
            elif score == '0' and counter[c] > 0 :
                # c is not in target and is duplicate
                # remove all postings with tf > counter[c]
                self._remove_duplicates(c, counter[c])
            else :
                # c is not in target and is not duplicate
                self._gray(unwanted_terms, c)
        
        #returns the inverted index posting lists pruned from the unwanted posting lists
        return {k:v for k,v in self._inverted_index._posting_lists.items() if k not in unwanted_terms}

    def _merge(self) -> List[int]:
        #5-out-of-N AND
        result = []
        posting_lists = [iter(p) for p in self._inverted_index._posting_lists.values()]

        required_minimum = 5

        all_cursors = [next(p, None) for p in posting_lists]
        remaining_cursor_ids = [i for i in range(len(all_cursors)) if all_cursors[i]]


        while len(remaining_cursor_ids) >= required_minimum:

            document_id = min(all_cursors[i].document_id for i in remaining_cursor_ids)
            frontier_cursor_ids = [i for i in remaining_cursor_ids if all_cursors[i].document_id == document_id]

            if len(frontier_cursor_ids) >= required_minimum:
                result.append(document_id)

            for i in frontier_cursor_ids:
                all_cursors[i] = next(posting_lists[i], None)
            remaining_cursor_ids = [i for i in range(len(all_cursors)) if all_cursors[i]]

        #returns a list of word indices
        return result

    def get_possible_matches(self, feedback, guess) :
        #should be called after every step of the wordler solver
        self._inverted_index._posting_lists = self._update_index(feedback, guess)
        return self._merge()
    

#Example:

def test_corpus() :
    guess = "speed" 
    corpus = in3120.InMemoryCorpus(filenames="answer-words.txt")

    solverengine = SolverSearchEngine(corpus)

    feedback = [('s', '0'), ('p', '0'), ('e', '1'), ('e', '0'), ('d', '0')]
    result = solverengine.get_possible_matches(feedback, guess)
    for i in result :
        print(corpus[i])

def test_behaviors() :
    feedbacks = [[('s', '0'), ('p', '0'), ('e', '1'), ('e', '0'), ('d', '1')],
    [('s', '1'), ('p', '0'), ('e', '1'), ('e', '1'), ('d', '0')],
    [('s', '2'), ('p', '0'), ('e', '2'), ('e', '0'), ('d', '0')],
    [('s', '0'), ('p', '1'), ('e', '2'), ('e', '1'), ('d', '0')]]
    corpora = [in3120.InMemoryCorpus().add_document(in3120.InMemoryDocument(0, {'body': 'abide'})),
    in3120.InMemoryCorpus().add_document(in3120.InMemoryDocument(0, {'body': 'erase'})),
    in3120.InMemoryCorpus().add_document(in3120.InMemoryDocument(0, {'body': 'steal'})),
    in3120.InMemoryCorpus().add_document(in3120.InMemoryDocument(0, {'body': 'crepe'}))]

    for i in range(4) :
        solverengine = SolverSearchEngine(corpora[i])
        result = solverengine.get_possible_matches(feedbacks[i], "speed")
        for j in result :
            print(corpora[i][j])
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

    def _green(self, position: int, char: str) -> Set[Tuple[str,int]]:
        #returns all the words having a different letter at this position
        terms = set()
        for term, pos in self._inverted_index._posting_lists.keys():
            if pos == position and term != char :
                terms.add((term, pos))
        return terms 

    def _yellow(self, position: int, char: str) -> Set[Tuple[str,int]] :
        #returns all the words having the same letter at this position
        return {(char, position)}
        
    def _gray(self, char: str) -> Set[Tuple[str,int]]:
        #returns all the words having this letter
        terms = set()
        for term, pos in self._inverted_index._posting_lists.keys():
            if term == char :
                terms.add((term, pos))
        return terms

    def _update_index(self, feedback, guess) -> Dict[Tuple[str,int],List[in3120.Posting]]:
        # Example feedback format: [('a', '1'), ('b', '1'), ('a', '2'), ('c', '2'), ('k', '2')]
        unwanted_terms = set()
        term_freq = Counter(guess)

        for i, (c, score) in enumerate(feedback) :
            if score == '2' : # c is correct
                unwanted_terms = unwanted_terms| self._green(i, c)
            elif score == '0' and term_freq[c] < 2 : # c is not in target and is not duplicate
                unwanted_terms = unwanted_terms| self._gray(c)
            else :
                # c is in the wrong pos or c is duplicate
                unwanted_terms = unwanted_terms| self._yellow(i,c)
        
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

corpus = in3120.InMemoryCorpus(filenames="answer-words.txt")

solverengine = SolverSearchEngine(corpus)

guess = "aback"
feedback = [('a', '0'), ('b', '1'), ('a', '2'), ('c', '2'), ('k', '2')]
result = solverengine.get_possible_matches(feedback, guess)
for i in result :
    print(corpus[i])
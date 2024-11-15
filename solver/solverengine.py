from collections import Counter
from typing import Dict, List, Set, Tuple
from wordleinvertedindex import MyInvertedIndex
from context import in3120

class SolverSearchEngine :

    def __init__(self, corpus: in3120.Corpus) -> None:
        """
        class that, from a feedback and the guessed word, returns a list of indices of all the possible words using get_possible_matches()
        """
        self._corpus = corpus
        self._inverted_index = MyInvertedIndex(self._corpus)

    def _green(self, unwanted_terms: Set, position: int, char: str) -> Set[Tuple[str,int]]:
        #returns all the words having a different letter at this position
        for term, pos in self._inverted_index._posting_lists.keys():
            if pos == position and term != char :
                unwanted_terms.add((term, pos))

    def _yellow(self, unwanted_terms: Set, position: int, char: str) -> Set[Tuple[str,int]] :
        #should remove all the words that don't contain the letter c
        #returns all the words having the same letter at this position
        unwanted_terms.add((char, position))
        
    def _gray(self, unwanted_terms: Set, char: str) -> Set[Tuple[str,int]]:
        #returns all the words having this letter
        for term, pos in self._inverted_index._posting_lists.keys():
            if term == char :
                unwanted_terms.add((term, pos))

    def _get_letter_counts(self, feedback) :
        """
        letter counts: all the letters that have to be included and that the amount of them
        for the feedback [('a', '0'), ('b', '1'), ('a', '2'), ('c', '2'), ('k', '2')]
        we have:

        letter: (number of non-gray; number of gray) 
        {
        "a" : 2, 1
        "b" : 1, 0
        "c" : 1, 0
        "k" : 1, 0
        }
        
        """
        correct = [c for c, n in feedback if n!='0']
        counter_1 = Counter(c for c,_ in feedback)
        counter_2 = Counter(c for c,n in feedback if n=='0')

        return {c:(counter_1[c],counter_2[c]) for c in correct if c in correct}

    def _update_index(self, feedback, guess) -> Dict[Tuple[str,int],List[in3120.Posting]]:
        # Example feedback format: [('a', '0'), ('b', '1'), ('a', '2'), ('c', '2'), ('k', '2')]
        unwanted_terms = set()
        char_counts = Counter(guess)
    
        """
        checks if in the frontier:
            green: c at that pos 
            yellow: at least one c but no at that pos 
            gray:
                there's only X c in the word
                there's only X c in the word and it's not at that pos
                there's no c in the word
        
        """

        for i, (c, score) in enumerate(feedback) :
            if score == '2' :
                self._green(unwanted_terms, i, c)
            elif score == '1' :
                self._yellow(unwanted_terms, i,c)
            elif score == '0' and char_counts[c] > 1 :
                self._yellow(unwanted_terms, i,c)
            else :    
                self._gray(unwanted_terms, c)
        
        #returns the inverted index posting lists pruned from the unwanted posting lists
        return {k:v for k,v in self._inverted_index._posting_lists.items() if k not in unwanted_terms}

    def _is_in_range(self, letter_counts, word) :
        term_freq = Counter(word)
        for c in letter_counts :
            r1, r2 = letter_counts[c]
            if r2 == 0 :
                if term_freq[c] < r1 :
                    return False
            else :
                if term_freq[c] != r1-r2 :
                    return False
        return True
                
    def _merge(self, letter_counts) -> List[int]:
        #5-out-of-N AND
        result = []
        posting_lists = [iter(p) for p in self._inverted_index._posting_lists.values()]

        required_minimum = 5

        all_cursors = [next(p, None) for p in posting_lists] #all postings of a layer
        remaining_cursor_ids = [i for i in range(len(all_cursors)) if all_cursors[i]] #remaining posting_list iter (not none)


        while len(remaining_cursor_ids) >= required_minimum:

            document_id = min(all_cursors[i].document_id for i in remaining_cursor_ids)
            frontier_cursor_ids = [i for i in remaining_cursor_ids if all_cursors[i].document_id == document_id]

            if len(frontier_cursor_ids) >= required_minimum :
                
                word = self._corpus[document_id].get_field("body", "")
                if all(c in word for c in letter_counts) : 
                    if self._is_in_range(letter_counts, word) :
                    # checks if the word contains all the green and yellow letters and in the right amount.
                        result.append(document_id)
        

            for i in frontier_cursor_ids:
                all_cursors[i] = next(posting_lists[i], None)
            remaining_cursor_ids = [i for i in range(len(all_cursors)) if all_cursors[i]]

        #returns a list of word indices
        return result

    def get_possible_matches(self, feedback, guess) :
        #should be called after every step of the wordler solver
        self._inverted_index._posting_lists = self._update_index(feedback, guess)
        letter_counts = self._get_letter_counts(feedback)
        print(letter_counts)
        return self._merge(letter_counts)
    

#Example:

def test_corpus(guess, feedback) :
    # guess = "aback" 
    corpus = in3120.InMemoryCorpus(filenames="answer-words.txt")

    solverengine = SolverSearchEngine(corpus)

    # feedback = [('a', '0'), ('b', '1'), ('a', '2'), ('c', '2'), ('k', '2')]
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

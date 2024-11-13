from optparse import Option
from typing import List, Optional


class WordleRanker:
    """
    A ranker optimized for Wordle by scoring based on letter frequency and positional feedback.
    """

    def __init__(self, candidate_words: List[str]):
        self.__scores = {}
        self.__candidate_words = candidate_words

    def reset(self):
        self.__scores.clear()

    def update_scores(self, filtered_wordlist: List[str] | None = None):
        """
        Update scores for all candidate words based on letter and position frequencies.
        """
        assert self.__scores == {}
        candidate_words = self.__candidate_words or filtered_wordlist

        letter_position_counts = [{} for _ in range(5)]
        letter_counts = {}

        for word in candidate_words:
            for position, letter in enumerate(word):
                letter_counts[letter] = letter_counts.get(letter, 0) + 1
                if letter not in letter_position_counts[position]:
                    letter_position_counts[position][letter] = 0
                letter_position_counts[position][letter] += 1

        for word in candidate_words:
            score = 0
            for position, letter in enumerate(word):
                score += letter_counts[letter] + letter_position_counts[position].get(letter, 0)
            self.__scores[word] = score

    def rank(self) -> List[str]:
        """
        Rank candidate words by score (higher is better).
        """
        # Sort candidates by score in descending order
        return sorted(self.__scores.keys(), key=lambda word: self.__scores[word], reverse=True)
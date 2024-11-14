# Import the necessary modules
from functools import reduce

from context import in3120
from in3120 import Posting, PostingsMerger

"""
Plan:
    Corpus -> alle ord -> invertedindex -> alle ord, men single letters
    get_feedback -> fetch all docs where letter from based on feedback, get doc_id -> sparseDocVector -> cosine
    order based on cosine, return new list of accepted words -> new guess and repeat
"""


class WordleSolver:
    def __init__(self):
        """
        Initialize the Wordle solver with a list of valid words.
        """
        self.corpus = in3120.InMemoryCorpus(filenames="answer-words.txt")
        self.tokenizer = in3120.UnigramTokenizer()
        self.invertedindex = in3120.InMemoryInvertedIndex(
            corpus=self.corpus,
            normalizer=in3120.SimpleNormalizer(),
            tokenizer=self.tokenizer,
            fields=["body"],
        )
        self.wordindex = in3120.InMemoryInvertedIndex(
            corpus=self.corpus,
            normalizer=in3120.SimpleNormalizer(),
            tokenizer=in3120.SimpleTokenizer(),
            fields=["body"],
        )
        self.vectorizer = in3120.Vectorizer(
            self.corpus, self.invertedindex, in3120.Trie()
        )

        # sparsevector = self.vectorizer.from_document(self.corpus.get_document(doc_id), fields=["body"]).cosine(OTHER)
        self.ranker = in3120.WordleRanker(
            self.corpus, self.invertedindex, self.vectorizer
        )

        # for x in self.invertedindex.get_postings_iterator("a"):
        #     print(x)
        self.candidates = [
            (
                word.get_field("body", ""),
                *list(self.wordindex[word.get_field("body", "")]),
            )
            for word in self.corpus
        ]
        # for e in self.candidates:
        #     print(e)

        self.target_word = "abase"
        # self.rank_candidates_by_similarity(
        #     candidates=self.candidates, guess=(self.target_word)
        # )
        self.first_guess = "crane"

    def rank_candidates_by_similarity(
        self, candidates: list[tuple[str, Posting]], guess: str
    ):
        ranked_candidates = []
        guess_doc_id = self.wordindex[guess]

        self.ranker.reset(guess_doc_id)
        for candidate in candidates:
            self.ranker.update(guess, 0, candidate[1])
            ranked_candidates.append((candidate[0], self.ranker.evaluate()))
            self.ranker.reset(guess_doc_id)

        ranked_candidates.sort(key=lambda x: x[1])
        return [candidate for candidate, _ in ranked_candidates]

    def filter_candidates(self, feedback):
        """
        Filters candidates based on the feedback from a guess.

        feedback is a list of tuples with (letter, status) where:
        - '2' indicates green (correct position),
        - '1' indicates yellow (wrong position),
        - '0' indicates gray (letter not in word).
        """
        self.first_guess
        pass

    def guess_word(self):
        """
        Make the next guess from the list of ranked candidates.
        """
        ranked_candidates = self.rank_candidates_by_similarity(
            self.candidates, self.first_guess
        )

        return ranked_candidates[0] if ranked_candidates else None

    def solve(self, max_attempts=6):
        """
        Solve the Wordle game by iterating through guesses until the solution is found
        or maximum attempts are reached.
        """
        for attempt in range(max_attempts):
            guess = self.first_guess if attempt == 0 else self.guess_word()
            if guess is None:
                print("No valid candidates left.")
                return None

            print(f"Attempt {attempt + 1}: Guessing '{guess}'")

            # Placeholder
            feedback = self.get_feedback(guess)

            if all(status == "2" for _, status in feedback):
                print(f"Solution found in {attempt + 1} attempts: {guess}")
                return guess

            self.filter_candidates(guess, feedback)

        print("Max attempts reached. Solution not found.")
        return None

    def get_feedback(self, guess):
        """
        Placeholder function to simulate feedback for a given guess.
        This should be replaced by actual feedback from the Wordle game.

        Returns:
        A list of tuples (letter, status: [0, 1, 2]) representing the feedback for each letter.
        """

        # Example feedback format: [('c', '2'), ('a', '0'), ('r', '1'), ('e', '0'), ('s', '2')]
        feedback = []
        unmatched_letters = list(self.target_word)

        for idx, letter in enumerate(guess):
            if letter == self.target_word[idx]:
                feedback.append((letter, "2"))
                unmatched_letters[idx] = None
            else:
                feedback.append((letter, None))

        for idx, (letter, status) in enumerate(feedback):
            if status is not None:
                continue

            if letter in unmatched_letters:
                feedback[idx] = (letter, "1")
                unmatched_letters[unmatched_letters.index(letter)] = None
            else:
                feedback[idx] = (letter, "0")

        return feedback

from copy import deepcopy

from context import in3120
from solver.solverengine import SolverSearchEngine

"""
Plan:
    Corpus -> alle ord -> invertedindex -> alle ord, men single letters
    get_feedback -> fetch all docs where letter from based on feedback, get doc_id -> sparseDocVector -> cosine
    order based on cosine, return new list of accepted words -> new guess and repeat
"""


class WordleSolver:
    def __init__(self, debug: bool = False):
        """
        Initialize the Wordle solver with a list of valid words.
        """
        self.debug = debug
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
        self.all_words = set(word.get_field("body", "") for word in self.corpus)

        self.candidates = deepcopy(self.all_words)
        self.word_vectors = self._cache_word_vectors()

        self.engine = SolverSearchEngine(self.corpus, self.candidates, self.debug)

        self.target_word = None
        self.first_guess = "slate"

    def _cache_word_vectors(self):
        """
        Cache vector representations for all words in the corpus.
        """
        cache = {}
        for word in self.candidates:
            document_id = list(self.wordindex[word])[0].document_id
            cache[word] = self.vectorizer.from_document(
                self.corpus.get_document(document_id), ["body"]
            )
        return cache

    def rank_candidates_by_similarity(self, candidates: set[str], guess: str):
        return [
            candidate
            for candidate, _ in sorted(
                [
                    (
                        candidate,
                        self.word_vectors[guess].cosine(self.word_vectors[candidate]),
                    )
                    for candidate in candidates
                ],
                key=lambda x: x[1],
            )
        ]

    def filter_candidates(self, feedback, guess):
        """
        Filters candidates based on the feedback from a guess.

        feedback is a list of tuples with (letter, status) where:
        - '2' indicates green (correct position),
        - '1' indicates yellow (wrong position),
        - '0' indicates gray (letter not in word).
        """
        possible_indices = self.engine.get_possible_matches(feedback, guess)
        self.candidates = [
            self.corpus.get_document(idx).get_field("body", "")
            for idx in possible_indices
        ]

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
        if self.target_word is None:
            print("Target word not set, exiting")
        for attempt in range(max_attempts):
            """
            Tenkte at for hvert attempt, vi har en funksjon som bestemmer hvor mye vi skal explore.
            når attempt er lav vi kan:
                - velge at random et ord fra lista generert av solverengine.get_possible_matches(feedback, guess)
                - velge ordet med lavest cosin likhet
            Men når attempt er høy:
                - velge ordet med høyest cosin likhet (Det er det den gjør allerede vel?)
            """
            guess = self.first_guess if attempt == 0 else self.guess_word()
            if guess is None:
                print("No valid candidates left.")
                return {
                    "success": False,
                    "attempts": attempt,
                    "target_word": self.target_word,
                }

            print(f"Attempt {attempt + 1}: Guessing '{guess}'")

            feedback = self.get_feedback(guess)

            if all(status == "2" for _, status in feedback):
                print(f"Solution found in {attempt + 1} attempts: {guess}")
                return {
                    "success": True,
                    "attempts": attempt + 1,
                    "target_word": self.target_word,
                }

            self.filter_candidates(feedback, guess)

        print("Max attempts reached. Solution not found.")
        return {
            "success": False,
            "attempts": max_attempts,
            "target_word": self.target_word,
        }

    def get_feedback(self, guess):
        """
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

    def reset(self, new_word: str) -> None:
        self.target_word = new_word
        self.candidates = deepcopy(self.all_words)
        self.engine = SolverSearchEngine(self.corpus, self.candidates, self.debug)

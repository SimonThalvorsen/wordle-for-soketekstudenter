# Import the necessary modules
import random

from context import in3120

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
        # self.ranker = in3120.WordleRanker(
        #     self.corpus, self.invertedindex, self.vectorizer
        # )

        self.candidates = [word.get_field("body", "") for word in self.corpus]

        # doc = self.corpus.get_document(random.randint(0, self.corpus.size()))
        # self.target_word = doc.get_field("body", "")
        # print("Target word:", self.target_word)
        self.first_guess = "slate"

    def rank_candidates_by_similarity(self, candidates: list[str], guess: str):
        ranked_candidates = []
        guess_vector = self.vectorizer.from_document(
            self.corpus.get_document(list(self.wordindex[guess])[0].document_id),
            ["body"],
        )
        for candidate in candidates:
            candidate_vector = self.vectorizer.from_document(
                self.corpus.get_document(
                    list(self.wordindex[candidate])[0].document_id
                ),
                ["body"],
            )
            ranked_candidates.append((candidate, guess_vector.cosine(candidate_vector)))

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
        filtered_candidates = []
        for candidate in self.candidates:
            match = True
            for idx, (letter, status) in enumerate(feedback):
                if status == "2":  # Green - correct position
                    if candidate[idx] != letter:
                        match = False
                        break
                elif status == "1":  # Yellow - wrong position
                    if letter not in candidate or candidate[idx] == letter:
                        match = False
                        break
                elif status == "0":  # Gray - not in word
                    if letter in candidate:
                        match = False
                        break
            if match:
                filtered_candidates.append(candidate)

        self.candidates = filtered_candidates

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

            self.filter_candidates(feedback)

        print("Max attempts reached. Solution not found.")
        return {
            "success": False,
            "attempts": max_attempts,
            "target_word": self.target_word,
        }

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

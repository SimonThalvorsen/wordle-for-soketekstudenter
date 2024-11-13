# Import the necessary modules
from assignments.in3120 import Document, InMemoryDocument
from .corpus import InMemoryCorpus
from .dictionary import InMemoryDictionary
from .tokenizer import SimpleTokenizer
from .normalizer import SimpleNormalizer
from .stringfinder import StringFinder
from .betterranker import BetterRanker
from .wildcardexpander import WildcardExpander


class WordleSolver:
    def __init__(self, word_list):
        """
        Initialize the Wordle solver with a list of valid words.
        """
        # Load the corpus and dictionary
        self.corpus = InMemoryCorpus(filenames=[""])  # Corpus of all valid five-letter words
        self.dictionary = InMemoryDictionary()  # Dictionary to validate words

        # Initialize other components
        self.tokenizer = SimpleTokenizer()
        self.normalizer = SimpleNormalizer()
        self.trie = StringFinder()  # Used for pattern matching
        self.ranker = BetterRanker(self.corpus)  # Used to prioritize guesses
        self.wildcard_expander = WildcardExpander()

        # Add words to trie for fast pattern matching
        for word in word_list:
            self.trie.insert(word)

        # Maintain a list of remaining candidate words
        self.candidates = set(word_list)

    def normalize_word(self, word):
        """
        Normalize the word to a consistent format (e.g., lowercase).
        """
        return self.normalizer.normalize(word)

    def filter_candidates(self, guess, feedback):
        """
        Filters candidates based on the feedback from a guess.

        feedback is a list of tuples with (letter, status) where:
        - 'G' indicates green (correct position),
        - 'Y' indicates yellow (wrong position),
        - 'B' indicates gray (letter not in word).
        """
        new_candidates = set()

        for word in self.candidates:
            match = True
            for idx, (letter, status) in enumerate(feedback):
                if status == "G":  # Green
                    if word[idx] != letter:
                        match = False
                        break
                elif status == "Y":  # Yellow
                    if letter not in word or word[idx] == letter:
                        match = False
                        break
                elif status == "B":  # Gray
                    if letter in word:
                        match = False
                        break

            if match:
                new_candidates.add(word)

        # Update the candidates list
        self.candidates = new_candidates

    def rank_candidates(self):
        """
        Rank the remaining candidates and choose the best guess.
        """
        # Placeholder for ranking function, using frequency analysis as an example
        # Rank candidates based on their usefulness in revealing new letters
        # Adjust ranking logic as needed
        ranked_candidates = self.ranker.rank(self.candidates)
        return ranked_candidates[0] if ranked_candidates else None

    def guess_word(self):
        """
        Make the next guess from the list of ranked candidates.
        """
        return self.rank_candidates()

    def solve(self, max_attempts=6):
        """
        Solve the Wordle game by iterating through guesses until the solution is found
        or maximum attempts are reached.
        """
        for attempt in range(max_attempts):
            # Choose the best word to guess based on ranking
            guess = self.guess_word()
            if guess is None:
                print("No valid candidates left.")
                return None

            print(f"Attempt {attempt + 1}: Guessing '{guess}'")

            # Placeholder: replace with actual feedback from Wordle game environment
            feedback = self.get_feedback(
                guess
            )  # Simulate feedback as list of (letter, status)

            # If all letters are green, we found the solution
            if all(status == "G" for _, status in feedback):
                print(f"Solution found in {attempt + 1} attempts: {guess}")
                return guess

            # Filter candidates based on feedback
            self.filter_candidates(guess, feedback)

        print("Max attempts reached. Solution not found.")
        return None

    def get_feedback(self, guess):
        """
        Placeholder function to simulate feedback for a given guess.
        This should be replaced by actual feedback from the Wordle game.

        Returns:
        A list of tuples (letter, status) representing the feedback for each letter.
        """
        # Example feedback format: [('c', 'G'), ('a', 'B'), ('r', 'Y'), ('e', 'B'), ('s', 'G')]
        feedback = (
            []
        )  # Placeholder - populate based on Wordle game's response to `guess`
        return feedback

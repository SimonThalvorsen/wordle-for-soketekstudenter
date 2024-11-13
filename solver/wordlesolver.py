# Import the necessary modules

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
        self.vectorizer = in3120.Vectorizer(
            self.corpus, self.invertedindex, in3120.Trie()
        )
        print(len(self.corpus))
        val = []
        for x in self.invertedindex.get_postings_iterator(
            list(self.invertedindex.get_indexed_terms())[0]
        ):
            val.append(
                (
                    self.corpus.get_document(x.document_id).get_field("body", ""),
                    self.vectorizer.from_document(
                        self.corpus.get_document(x.document_id), ["body"]
                    ),
                )
            )
        #val.sort(key=lambda s: s[1], reverse=True)
        #print(val)
        print(len(val))
        print(val[0][1].cosine(val[1][1]))

        """
        for x in self.invertedindex.get_indexed_terms():
            print(x, self.invertedindex.get_document_frequency(x))
            # out: letter, numDocumentsOccurs
            for y in self.invertedindex.get_postings_iterator(x):
                print(y)
                out: doc_id, term_freq
        """

        self.ranker = in3120.WordleRanker(
            [doc.get_field("body", "") for doc in self.corpus]
        )

        self.candidates = [doc.get_field("body", "") for doc in self.corpus]
        self.target_word = "crane"

    def rank_candidates_by_similarity(self, candidates, guess):
        guess_vector = self.vectorizer.from_document(guess, fields=["body"])
        ranked_candidates = []

        for candidate in candidates:
            candidate_vector = self.vectorizer.from_document(candidate, fields=["body"])
            similarity = guess_vector.cosine(candidate_vector)
            ranked_candidates.append((candidate, similarity))

        ranked_candidates.sort(key=lambda x: x[1], reverse=True)
        return [candidate for candidate, _ in ranked_candidates]

    def filter_candidates(self, guess, feedback):
        """
        Filters candidates based on the feedback from a guess.

        feedback is a list of tuples with (letter, status) where:
        - '2' indicates green (correct position),
        - '1' indicates yellow (wrong position),
        - '0' indicates gray (letter not in word).
        """

    def rank_candidates(self):
        """
        Rank the remaining candidates and choose the best guess.
        """
        self.ranker.update_scores(self.candidates)
        ranked_candidates = self.ranker.rank()
        self.ranker.reset()
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
            guess = "resin" if attempt == 0 else self.guess_word()
            if guess is None:
                print("No valid candidates left.")
                return None

            print(f"Attempt {attempt + 1}: Guessing '{guess}'")

            # Placeholder
            feedback = self.get_feedback(guess)

            # If all letters are green, we found the solution
            if all(status == "2" for _, status in feedback):
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

# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long

from __future__ import annotations

from _collections_abc import Iterator, Iterable
from math import sqrt

from .sieve import Sieve


class SparseDocumentVector:
    """
    A simple representation of a sparse document vector. The vector space has one dimension
    per vocabulary term, and our representation only lists the dimensions that have non-zero
    values.

    Being able to place text buffers, be they documents or queries, in a vector space and
    thinking of them as point clouds (or, equivalently, as vectors from the origin) enables us
    to numerically assess how similar they are according to some suitable metric. Cosine
    similarity (the inner product of the vectors normalized by their lengths) is a very
    common metric.
    """

    def __init__(self, values: dict[str, float]):
        # An alternative, effective representation would be as a
        # [(term identifier, weight)] list kept sorted by integer
        # term identifiers. Computing dot products would then be done
        # pretty much in the same way we do posting list AND-scans.
        self._values = {term: weight for term, weight in values.items() if weight}

        # We cache the length. It might get used over and over, e.g., for cosine
        # computations. A value of None triggers lazy computation.
        self._length: float | None = None

    def __iter__(self):
        return iter(self._values.items())

    def __getitem__(self, term: str) -> float:
        return self._values.get(term, 0.0)

    def __setitem__(self, term: str, weight: float) -> None:
        self._values[term] = weight
        self._length = None

    def __contains__(self, term: str) -> bool:
        return term in self._values

    def __len__(self) -> int:
        """
        Enables use of the built-in len/1 function to count the number of non-zero
        dimensions in the vector. It is not for computing the vector's norm.
        """
        return len(self._values)

    def get_length(self) -> float:
        """
        Returns the length (L^2 norm, also called the Euclidian norm) of the vector.
        """
        if self._length:
            return self._length

        self._length = sqrt(sum(weight**2 for weight in self._values.values()))
        return self._length

    def normalize(self) -> None:
        """
        Divides all weights by the length of the vector, thus rescaling it to
        have unit length.
        """
        length = self.get_length()
        if length != 0:
            for term in self._values:
                self._values[term] /= length
        self._length = None


    def top(self, count: int) -> Iterable[tuple[str, float]]:
        """
        Returns the top weighted terms, i.e., the "most important" terms and their weights.
        """
        if count == 0:
            return []

        sieve = Sieve(count)
        sieve.sift2((weight, term) for term, weight in self._values.items())

        return [(term, weight) for weight, term in sieve.winners()]

    def truncate(self, count: int) -> None:
        """
        Truncates the vector so that it contains no more than the given number of terms,
        by removing the lowest-weighted terms.
        """
        if len(self._values) > count:
            self._values = dict(self.top(count))
        self._length = None

    def scale(self, factor: float) -> None:
        """
        Multiplies every vector component by the given factor.
        """
        if factor == 0:
            self._values.clear()
        else:
            for term in self._values:
                self._values[term] *= factor
                if self._values[term] == 0:
                    del self._values[term]
        self._length = None

    def dot(self, other: SparseDocumentVector) -> float:
        """
        Returns the dot product (inner product, scalar product) between this vector
        and the other vector.
        """
        return sum(
            self[term] * other[term] for term in self._values if term in other._values
        )

    def cosine(self, other: SparseDocumentVector) -> float:
        """
        Returns the cosine of the angle between this vector and the other vector.
        See also https://en.wikipedia.org/wiki/Cosine_similarity.
        """
        denominator = self.get_length() * other.get_length()
        if denominator == 0:
            return 0.0
        return self.dot(other) / denominator

    @staticmethod
    def centroid(vectors: Iterator[SparseDocumentVector]) -> SparseDocumentVector:
        """
        Computes the centroid of all the vectors, i.e., the average vector.
        """
        sum_vector = {}
        count = 0
        for vector in vectors:
            count += 1
            for term, weight in vector:
                if term in sum_vector:
                    sum_vector[term] += weight
                else:
                    sum_vector[term] = weight
        return SparseDocumentVector(
            {term: weight / count for term, weight in sum_vector.items()}
        )

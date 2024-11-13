# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long
# pylint: disable=too-few-public-methods

from typing import Iterator, Dict, Any

from jinja2.utils import consume

from .normalizer import Normalizer
from .tokenizer import Tokenizer
from .trie import Trie


class StringFinder:
    """
    Given a trie encoding a dictionary of strings, efficiently finds the subset of strings in the dictionary
    that are also present in a given text buffer. I.e., in a sense computes the "intersection" or "overlap"
    between the dictionary and the text buffer.

    Uses a trie-walk algorithm similar to the Aho-Corasick algorithm with some simplifications and some minor
    NLP extensions. The running time of this algorithm is virtually independent of the size of the dictionary,
    and linear in the length of the buffer we are searching in.

    The tokenizer we use when scanning the input buffer is assumed to be the same as the one that was used
    when adding strings to the trie.
    """

    def __init__(self, trie: Trie, normalizer: Normalizer, tokenizer: Tokenizer):
        self.__trie = trie
        self.__normalizer = normalizer  # The same as was used for trie building.
        self.__tokenizer = tokenizer  # The same as was used for trie building.

    def scan(self, buffer: str) -> Iterator[dict[str, Any]]:
        """
        Scans the given buffer and finds all dictionary entries in the trie that are also present in the
        buffer. We only consider matches that begin and end on token boundaries.

        The matches, if any, are yielded back to the client as dictionaries having the keys "match" (str),
        "surface" (str), "meta" (Optional[Any]), and "span" (Tuple[int, int]). Note that "match" refers to
        the matching dictionary entry, "surface" refers to the content of the input buffer that triggered the
        match (the surface form), and "span" refers to the exact location in the input buffer where the surface
        form is found. Depending on the normalizer that is used, "match" and "surface" may or may not differ.

        A space-normalized version of the surface form is emitted as "surface", for convenience. Clients
        that require an exact surface form that is not space-normalized can easily reconstruct the desired
        string using the emitted "span" value.

        In a serious application we'd add more lookup/evaluation features, e.g., support for prefix matching,
        support for leftmost-longest matching (instead of reporting all matches), and more.
        """


        ## NOTE: hadde denne printen i koden mens jeg testet og da fungerte alt som forventet,
        # Var ikke før jeg skulle gjøre koden klar til levering at jeg oppdaget denne forskjellen, ettersom alle
        # testene <<passerte>> på min maskin hvis printen var der.
        # Litt sånn spurious verdier, har også  fungert på ifi-maskin

        """
        Med print: (linje 81)
        9.549991227686405e-05 8.639995940029621e-05
        1.105323578155948 -> 0.7553235781559481
        ratio                ratio - slack
        
        Uten print:
        1.9799917936325073e-05 1.4100223779678345e-05
        1.404227212681638 -> 1.054227212681638
        ratio                ratio - slack
        """

        tokens = self.__tokenizer.tokens(buffer)
        active_states = []  # Format (0: Node, 1: Span, 2: surface, 3: match)

        for token, span in tokens:
            new_active_states = []
            normalized_token = self.__normalizer.normalize(token)

            # Consume states
            for tuple in active_states:
                node = tuple[0].consume(" " + normalized_token)
                if node:
                    #print(tuple[2]) ##NOTE: er altså denne det er snakk om
                    new_active_states.append((node, (tuple[1][0], span[1]), f"{tuple[2]} {token}", f"{tuple[3]} {normalized_token}"))
                    continue

                node = tuple[0].consume(normalized_token)
                if node:
                    new_active_states.append((node, (tuple[1][0], span[1]), tuple[2] + token, tuple[3] + normalized_token))


            # Consume root
            node = self.__trie
            node = node.consume(normalized_token)
            if node:
                new_active_states.append((node, span, token, normalized_token))


            active_states = new_active_states
            for node, start_span, surface, match in active_states:
                if node.is_final():
                    yield {
                        "match": match,
                        "surface": surface,
                        "meta": node.get_meta(),
                        "span": start_span
                    }

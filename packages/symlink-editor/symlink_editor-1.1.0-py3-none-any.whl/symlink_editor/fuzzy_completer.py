from __future__ import annotations

import os
import re
import enum
from typing import Callable, Iterable, NamedTuple, Sequence

from prompt_toolkit.document import Document
from prompt_toolkit.filters import FilterOrBool, to_filter
from prompt_toolkit.formatted_text import AnyFormattedText, StyleAndTextTuples
from prompt_toolkit.completion import CompleteEvent, Completer, Completion, PathCompleter

__all__ = [
    "FuzzyCompleter",
    "FuzzyPathCompleter",
]


class CompleterMatch(enum.Enum):
    START = enum.auto()
    CONTAINS = enum.auto()
    FUZZY = enum.auto()

class BoolWithAuto(enum.Enum):
    TRUE = enum.auto()
    FALSE = enum.auto()
    AUTO = enum.auto()


class FuzzyCompleter(Completer):
    """
    Fuzzy completion.
    This wraps any other completer and turns it into a fuzzy completer.

    With CompleterMatch.FUZZY:
    If the list of words is: ["leopard" , "gorilla", "dinosaur", "cat", "bee"]
    Then trying to complete "oar" would yield "leopard" and "dinosaur", but not
    the others, because they match the regular expression 'o.*a.*r'.
    Similar, in another application "djm" could expand to "django_migrations".

    The results are sorted by relevance, which is defined as the start position
    and the length of the match.

    Notice that this is not really a tool to work around spelling mistakes,
    like what would be possible with difflib. The purpose is rather to have a
    quicker or more intuitive way to filter the given completions, especially
    when many completions have a common prefix.

    This is based on:
    https://github.com/prompt-toolkit/python-prompt-toolkit/blob/d8adbe9bfcf5f7e95b015d8ab12e2985b9a7822b/src/prompt_toolkit/completion/fuzzy_completer.py

    With CompleterMatch.CONTAINS:
    Completions must contain the input without additional characters in between.
    If the list of words is: ["leopard" , "gorilla", "dinosaur", "cat", "bee", "boar"]
    Then trying to complete "oar" would only yield "boar".

    With CompleterMatch.CONTAINS:
    Completions must start with the input.
    If the list of words is: ["leopard" , "gorilla", "dinosaur", "cat", "bee", "boar"]
    Then trying to complete "oar" would yield no completions.

    :param completer: A :class:`~.Completer` instance.
    :param WORD: When True, use WORD characters.
    :param pattern: Regex pattern which selects the characters before the
        cursor that are considered for the fuzzy matching.
    :param completer_match: A :class:`CompleterMatch`, see the descriptions above.
    :param case_sensitive: AUTO is considered true if the word before the cursor contains upper case letters.
    """

    def __init__(
        self,
        completer: Completer,
        WORD: bool = False,
        pattern: str | None = None,
        completer_match: CompleterMatch = CompleterMatch.FUZZY,
        case_sensitive: BoolWithAuto | bool = BoolWithAuto.AUTO,
    ) -> None:
        assert pattern is None or pattern.startswith("^")

        self.completer = completer
        self.completer_match = completer_match
        self.case_sensitive = case_sensitive

        def _get_pattern() -> str:
            if pattern:
                return pattern
            if WORD:
                return r"[^\s]+"
            return "^[a-zA-Z0-9_]*"

        self.pattern = re.compile(_get_pattern())

    def _case_sensitive(self, word_before_cursor: str) -> bool:
        if self.case_sensitive is BoolWithAuto.TRUE:
            return True
        elif self.case_sensitive is BoolWithAuto.FALSE:
            return False
        elif self.case_sensitive is BoolWithAuto.AUTO:
            return not word_before_cursor.islower()
        else:
            return self.case_sensitive

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        word_before_cursor = document.get_word_before_cursor(
            pattern=re.compile(self.pattern)
        )

        # Get completions
        document2 = Document(
            text=document.text[: document.cursor_position - len(word_before_cursor)],
            cursor_position=document.cursor_position - len(word_before_cursor),
        )

        inner_completions = list(
            self.completer.get_completions(document2, complete_event)
        )

        fuzzy_matches: list[_FuzzyMatch] = []

        if word_before_cursor == "":
            # If word before the cursor is an empty string, consider all
            # completions, without filtering everything with an empty regex
            # pattern.
            fuzzy_matches = [_FuzzyMatch(0, 0, compl) for compl in inner_completions]
        else:
            if self.completer_match is CompleterMatch.FUZZY:
                pat = ".*?".join(map(re.escape, word_before_cursor))
                pat = f"(?=({pat}))"  # lookahead regex to manage overlapping matches
                if self._case_sensitive(word_before_cursor):
                    regex = re.compile(pat)
                else:
                    regex = re.compile(pat, re.IGNORECASE)
                def fmatch(compl: Completion) -> _FuzzyMatch | None:
                    matches = list(regex.finditer(compl.text))
                    if matches:
                        # Prefer the match, closest to the left, then shortest.
                        best = min(matches, key=lambda m: (m.start(), len(m.group(1))))
                        return _FuzzyMatch(len(best.group(1)), best.start(), compl)
                    else:
                        return None

            elif self.completer_match is CompleterMatch.CONTAINS:
                if self._case_sensitive(word_before_cursor):
                    def fmatch(compl: Completion) -> _FuzzyMatch | None:
                        i = compl.text.find(word_before_cursor)
                        if i >= 0:
                            return _FuzzyMatch(len(word_before_cursor), i, compl)
                        else:
                            return None
                else:
                    lower_word_before_cursor = word_before_cursor.lower()
                    def fmatch(compl: Completion) -> _FuzzyMatch | None:
                        i = compl.text.lower().find(lower_word_before_cursor)
                        if i >= 0:
                            return _FuzzyMatch(len(word_before_cursor), i, compl)
                        else:
                            return None

            elif self.completer_match is CompleterMatch.START:
                if self._case_sensitive(word_before_cursor):
                    def fmatch(compl: Completion) -> _FuzzyMatch | None:
                        if compl.text.startswith(word_before_cursor):
                            return _FuzzyMatch(len(compl.text), 0, compl)
                        else:
                            return None
                else:
                    lower_word_before_cursor = word_before_cursor.lower()
                    def fmatch(compl: Completion) -> _FuzzyMatch | None:
                        if compl.text.lower().startswith(lower_word_before_cursor):
                            return _FuzzyMatch(len(compl.text), 0, compl)
                        else:
                            return None

            else:
                print("ERROR: not implemented completer_match=%r" % self.completer_match)  #type: ignore [unreachable]  # make mypy complain if another Variant is added without handling it here
                raise NotImplementedError(self.completer_match)

            for compl in inner_completions:
                fuzzy_match = fmatch(compl)
                if fuzzy_match:
                    fuzzy_matches.append(fuzzy_match)

            if self.completer_match is not CompleterMatch.START:
                def sort_key(fuzzy_match: _FuzzyMatch) -> tuple[int, int]:
                    "Sort by start position, then by the length of the match."
                    return fuzzy_match.start_pos, fuzzy_match.match_length

                fuzzy_matches = sorted(fuzzy_matches, key=sort_key)

        for match in fuzzy_matches:
            # Include these completions, but set the correct `display`
            # attribute and `start_position`.
            yield Completion(
                text=match.completion.text,
                start_position=match.completion.start_position
                - len(word_before_cursor),
                # We access to private `_display_meta` attribute, because that one is lazy.
                display_meta=match.completion._display_meta,
                display=self._get_display(match, word_before_cursor),
                style=match.completion.style,
            )

    def _get_display(
        self, fuzzy_match: _FuzzyMatch, word_before_cursor: str
    ) -> AnyFormattedText:
        """
        Generate formatted text for the display label.
        """

        def get_display() -> AnyFormattedText:
            m = fuzzy_match
            word = m.completion.text

            if m.match_length == 0:
                # No highlighting when we have zero length matches (no input text).
                # In this case, use the original display text (which can include
                # additional styling or characters).
                return m.completion.display

            result: StyleAndTextTuples = []

            # Text before match.
            result.append(("class:fuzzymatch.outside", word[: m.start_pos]))

            # The match itself.
            characters = list(word_before_cursor)

            for c in word[m.start_pos : m.start_pos + m.match_length]:
                classname = "class:fuzzymatch.inside"
                if characters and c.lower() == characters[0].lower():
                    classname += ".character"
                    del characters[0]

                result.append((classname, c))

            # Text after match.
            result.append(
                ("class:fuzzymatch.outside", word[m.start_pos + m.match_length :])
            )

            return result

        return get_display()


class FuzzyPathCompleter(FuzzyCompleter):

    def __init__(self,
        completer_match: CompleterMatch = CompleterMatch.FUZZY,
        case_sensitive: BoolWithAuto | bool = BoolWithAuto.AUTO,
    ) -> None:
        super().__init__(
            completer = PathCompleter(),
            pattern = r'^([^%s]+)' % os.path.sep,
            completer_match = completer_match,
            case_sensitive = case_sensitive,
        )


class _FuzzyMatch(NamedTuple):
    match_length: int
    start_pos: int
    completion: Completion

from typing import Iterable
from regex import Match, Pattern
from abc import ABC, abstractmethod
from unicode_segment._segmenter_config import SegmenterConfig


class Segmenter(ABC):
    def segment(self, text: str) -> Iterable[tuple[int, str]]:
        """
        Split into the relevant type of segments at every break opportunity
        """
        prev_break = 0
        for i in self._find_breaks(text):
            t = text[prev_break:i]
            if not t:
                continue
            yield (prev_break, t)
            prev_break = i

    @property
    @abstractmethod
    def _config(self) -> SegmenterConfig:
        pass

    def _find_breaks(self, text: str) -> Iterable[int]:
        if not text:
            return

        candidates = (
            range(len(text) + 1)
            if self._config.break_candidates_pattern is None
            else self._find_break_candidates(
                text, self._config.break_candidates_pattern
            )
        )

        for i in candidates:
            match = self._config.pattern.match(text, i)
            if match is not None:
                yield i

    def _find_break_candidates(self, text: str, pattern: Pattern) -> Iterable[int]:
        for m in pattern.finditer(text):
            yield m.start()

    def _get_matched_rule(self, match: Match) -> str:
        return next(x for x in match.groupdict().items() if x[1] is not None)[0]

    def _get_all_matched_rules(self, text: str) -> Iterable[str]:
        """For debugging: yield all matched rules in the text"""
        if not text:
            return

        for i in range(len(text) + 1):
            match = self._config.debug_pattern.match(text, i)
            assert match is not None
            yield self._get_matched_rule(match)

import regex
from unicode_segment._segmenter import Segmenter
import pytest
from unicode_segment.grapheme import GraphemeSegmenter
from unicode_segment.sentence import SentenceSegmenter
from unicode_segment.word import WordSegmenter

alphabet = "".join([chr(i) for i in range(ord("a"), ord("z") + 1)])
r = regex.compile(r"(?<=\[)[\d.]+(?=\])")


def get_rule_names(comment: str, initial: str) -> list[str]:
    return [f"{initial}B{remap_rule(float(n))}" for n in r.findall(comment)]


def remap_rule(n: float) -> str:
    if n == 0.2:
        return "1"
    elif n == 0.3:
        return "2"
    elif n % 1 != 0:
        return f"{int(n)}{alphabet[int(round(n % 1, 1) * 10) - 1]}"

    return str(int(n))


def get_line_params(segmenter: Segmenter, test_file_name: str):
    with open(f"tests/test_data/{test_file_name}", "r", encoding="utf-8") as f:
        return [
            (
                segmenter,
                test_file_name,
                line,
            )
            for line in f.readlines()
            if line.strip() and not line.startswith("#")
        ]


# https://www.unicode.org/Public/17.0.0/ucd/auxiliary/<file_name>
params: list[tuple[Segmenter, str]] = [
    (GraphemeSegmenter(), "GraphemeBreakTest.txt"),
    (WordSegmenter(), "WordBreakTest.txt"),
    (SentenceSegmenter(), "SentenceBreakTest.txt"),
]


@pytest.mark.parametrize(
    "segmenter",
    [segmenter for (segmenter, _) in params],
)
def test_zero_case(segmenter: Segmenter):
    assert list(segmenter.segment("")) == []
    assert list(segmenter._find_breaks("")) == []


line_params = [
    param
    for segmenter, test_file_name in params
    for param in get_line_params(segmenter, test_file_name)
]


@pytest.mark.parametrize("segmenter,test_file_name,line", line_params)
def test_unicode_break_fixture(segmenter: Segmenter, test_file_name: str, line: str):
    [case, comment] = line.split("#", 1)

    expected_all = [
        "".join([chr(int(cp, 16)) for cp in part.split("×")]) if part.strip() else ""
        for part in case.split("÷")
    ]

    expected = [s for s in expected_all if s]

    joined = "".join(expected)
    actual = [s for _, s in segmenter.segment(joined)]

    expected_rules = get_rule_names(comment, test_file_name[0])
    actual_rules = list(segmenter._get_all_matched_rules(joined))

    assert actual == expected, "\n".join(
        [
            f"\x1b[0m{line}\x1b[0m"
            for line in [
                f"\x1b[31m{actual}\x1b[0m != \x1b[32m{expected}",
                "Expected rules:",
                f"-> \x1b[32m{expected_rules}",
                "Actual rules:",
                f"-> \x1b[31m{actual_rules}",
                f"\x1b[90m# {case.strip()}",
                f"\x1b[90m# {comment.strip()}",
            ]
        ]
    )

    assert actual_rules == expected_rules, f"{actual_rules} != {expected_rules}"

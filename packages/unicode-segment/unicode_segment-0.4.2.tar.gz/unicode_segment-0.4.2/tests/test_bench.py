from unicode_segment import SentenceSegmenter, WordSegmenter, GraphemeSegmenter
from unicode_segment._rule_parser import RuleParser
from unicode_segment._segmenter import Segmenter
from faker import Faker
import regex

SEED = 16070459220457221183


def run_benchmark(benchmark, segmenter: Segmenter):
    faker = Faker()
    faker.seed_instance(SEED)

    with open(
        f".benchmarks/regexes/{segmenter.__class__.__name__}.txt",
        "w",
        encoding="utf-8",
    ) as f:
        debug_pattern = segmenter._config.debug_pattern.pattern
        debug_pattern = regex.sub(r"(?=\|\(\?<\w+>)", r"\n", debug_pattern)

        f.write(
            "\n\n".join(
                [
                    f"pattern: {segmenter._config.pattern.pattern}",
                    f"debug_pattern:\n{debug_pattern}",
                    f"break_candidates_pattern: {
                        segmenter._config.break_candidates_pattern.pattern
                        if segmenter._config.break_candidates_pattern is not None
                        else '*'
                    }",
                ]
            )
            + "\n"
        )

    def run_test(text: str):
        list(segmenter.segment(text))

    def setup():
        text = faker.text(500)
        # return (args, kwargs) for `run_test`
        return (text,), {}

    benchmark.pedantic(run_test, setup=setup, rounds=100)


def test_sentence_segmenter_benchmark(benchmark):
    run_benchmark(benchmark, SentenceSegmenter())


def test_word_segmenter_benchmark(benchmark):
    run_benchmark(benchmark, WordSegmenter())


def test_grapheme_segmenter_benchmark(benchmark):
    run_benchmark(benchmark, GraphemeSegmenter())


def test_init_benchmark(benchmark):
    def run_test():
        # just use word rules as an example
        RuleParser(
            "WB",
            {
                "AHLetter": {"ALetter", "Hebrew_Letter"},
                "MidNumLetQ": {"MidNumLet", "Single_Quote"},
            },
            [
                # Break at the start and end of text, unless the text is empty.
                r"WB1	sot	÷	Any",
                r"WB2	Any	÷	eot",
                # Do not break within CRLF.
                r"WB3	CR	×	LF",
                # Otherwise break before and after Newlines (including CR and LF)
                r"WB3a	(Newline | CR | LF)	÷	 ",
                r"WB3b	 	÷	(Newline | CR | LF)",
                # Do not break within emoji zwj sequences.
                r"WB3c	ZWJ	×	\p{Extended_Pictographic}",
                # Keep horizontal whitespace together.
                r"WB3d	WSegSpace	×	WSegSpace",
                # Ignore Format and Extend characters, except after sot, CR, LF, and Newline. (See Section 6.2, Replacing Ignore Rules.) This also has the effect of: Any × (Format | Extend | ZWJ)
                r"WB4	X (Extend | Format | ZWJ)*	→	X",
                # Do not break between most letters.
                r"WB5	AHLetter	×	AHLetter",
                # Do not break letters across certain punctuation, such as within “e.g.” or “example.com”.
                r"WB6	AHLetter	×	(MidLetter | MidNumLetQ) AHLetter",
                r"WB7	AHLetter (MidLetter | MidNumLetQ)	×	AHLetter",
                r"WB7a	Hebrew_Letter	×	Single_Quote",
                r"WB7b	Hebrew_Letter	×	Double_Quote Hebrew_Letter",
                r"WB7c	Hebrew_Letter Double_Quote	×	Hebrew_Letter",
                # Do not break within sequences of digits, or digits adjacent to letters (“3a”, or “A3”).
                r"WB8	Numeric	×	Numeric",
                r"WB9	AHLetter	×	Numeric",
                r"WB10	Numeric	×	AHLetter",
                # Do not break within sequences, such as “3.2” or “3,456.789”.
                r"WB11	Numeric (MidNum | MidNumLetQ)	×	Numeric",
                r"WB12	Numeric	×	(MidNum | MidNumLetQ) Numeric",
                # Do not break between Katakana.
                r"WB13	Katakana	×	Katakana",
                # Do not break from extenders.
                r"WB13a	(AHLetter | Numeric | Katakana | ExtendNumLet)	×	ExtendNumLet",
                r"WB13b	ExtendNumLet	×	(AHLetter | Numeric | Katakana)",
                # Do not break within emoji flag sequences. That is, do not break between regional indicator (RI) symbols if there is an odd number of RI characters before the break point.
                r"WB15	sot (RI RI)* RI	×	RI",
                r"WB16	[^RI] (RI RI)* RI	×	RI",
                # Otherwise, break everywhere (including around ideographs).
                r"WB999	Any	÷	Any",
            ],
        ).build()

    benchmark.pedantic(run_test, rounds=100)

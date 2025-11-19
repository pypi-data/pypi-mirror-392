from unicode_segment.sentence import SentenceSegmenter

segmenter = SentenceSegmenter()


def test_sentence_segmenter_basic():
    # Example from https://www.regular-expressions.info/unicodeboundaries.html#sentence
    text = (
        '"Dr. John works at I.B.M., doesn\'t he?", asked Alice. "Yes," replied Charlie.'
    )
    # Note that the first split is wrong, but it's a known limitation of the Unicode algorithm that it can never
    # give 100% results due to abbreviations etc.
    expected = [
        (0, '"Dr. '),
        (5, "John works at I.B.M., doesn't he?\", asked Alice. "),
        (54, '"Yes," replied Charlie.'),
    ]
    actual = list(segmenter.segment(text))
    assert actual == expected


def test_sentence_segmenter_motivating_cases():
    text = "".join(
        [
            "This, that, the other thing, etc. Another sentence... A, b, c, etc., and ",
            "more. D, e, f, etc. and more. One, i. e. two. Three, i. e., four. Five, ",
            "i.e. six. You have 4.2 messages. Property access: `a.b.c`.",
        ]
    )

    segments = segmenter.segment(text)

    assert list(segments) == [
        (0, "This, that, the other thing, etc. "),
        (34, "Another sentence... "),
        (54, "A, b, c, etc., and more. "),
        (79, "D, e, f, etc. and more. "),
        (103, "One, i. e. two. "),
        (119, "Three, i. e., four. "),
        (139, "Five, i.e. six. "),
        (155, "You have 4.2 messages. "),
        (178, "Property access: `a.b.c`."),
    ]

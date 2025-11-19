from unicode_segment._rule_parser import RuleParser
from unicode_segment._segmenter_config import SegmenterConfig
from ._segmenter import Segmenter

_config: SegmenterConfig | None = None


class WordSegmenter(Segmenter):
    """
    [Unicode TR29](https://www.unicode.org/reports/tr29/#Word_Boundaries)
    compliant word segmenter.

    Note that this segmenter does not currently include or support any
    locale-specific tailoring, meaning it may be unsuitable for languages with
    non-trivial word segmentation rules (e.g., Thai, Japanese).
    """

    # Currently, `WordSegmenter` doesn't support locale-specific tailoring. As a result, config is the same for all
    # instances, so we can cache upon first instantiation.
    _config = (
        _config
        if _config is not None
        else RuleParser(
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
    )

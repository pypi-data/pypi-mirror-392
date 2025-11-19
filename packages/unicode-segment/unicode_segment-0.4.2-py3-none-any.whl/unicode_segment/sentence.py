from unicode_segment._rule_parser import RuleParser
from unicode_segment._segmenter_config import SegmenterConfig
from ._segmenter import Segmenter

_config: SegmenterConfig | None = None


class SentenceSegmenter(Segmenter):
    """
    [Unicode TR29](https://www.unicode.org/reports/tr29/#Sentence_Boundaries)
    compliant sentence segmenter
    """

    # Currently, `SentenceSegmenter` doesn't support locale-specific tailoring. As a result, config is the same for all
    # instances, so we can cache upon first instantiation.
    _config = (
        _config
        if _config is not None
        else RuleParser(
            "SB",
            {
                "ParaSep": {"Sep", "CR", "LF"},
                "SATerm": {"STerm", "ATerm"},
            },
            [
                # Break at the start and end of text, unless the text is empty.
                r"SB1	sot	÷	Any",
                r"SB2	Any	÷	eot",
                # Do not break within CRLF.
                r"SB3	CR	×	LF",
                # Break after paragraph separators.
                r"SB4	ParaSep	÷	 ",
                # Ignore Format and Extend characters, except after sot, ParaSep, and within CRLF. (See Section 6.2, Replacing Ignore Rules.) This also has the effect of: Any × (Format | Extend)
                r"SB5	X (Extend | Format)*	→	X",
                # Do not break after full stop in certain contexts. [See note below.]
                r"SB6	ATerm	×	Numeric",
                r"SB7	(Upper | Lower) ATerm	×	Upper",
                r"SB8	ATerm Close* Sp*	×	( ¬(OLetter | Upper | Lower | ParaSep | SATerm) )* Lower",
                r"SB8a	SATerm Close* Sp*	×	(SContinue | SATerm)",
                # Break after sentence terminators, but include closing punctuation, trailing spaces, and any paragraph separator. [See note below.]
                r"SB9	SATerm Close*	×	(Close | Sp | ParaSep)",
                r"SB10	SATerm Close* Sp*	×	(Sp | ParaSep)",
                r"SB11	SATerm Close* Sp* ParaSep?	÷	 ",
                # Otherwise, do not break.
                r"SB998	Any	×	Any",
            ],
        ).build()
    )

from unicode_segment._rule_parser import RuleParser
from unicode_segment._segmenter_config import SegmenterConfig
from ._segmenter import Segmenter

_config: SegmenterConfig | None = None


class GraphemeSegmenter(Segmenter):
    """
    [Unicode TR29](https://www.unicode.org/reports/tr29/#Grapheme_Cluster_Boundaries)
    compliant grapheme segmenter
    """

    # Currently, `GraphemeSegmenter` doesn't support locale-specific tailoring. As a result, config is the same for all
    # instances, so we can cache upon first instantiation.
    _config = (
        _config
        if _config is not None
        else RuleParser(
            "GCB",
            {},
            [
                # Break at the start and end of text, unless the text is empty.
                r"GB1	sot	÷	Any",
                r"GB2	Any	÷	eot",
                # Do not break between a CR and LF. Otherwise, break before and after controls.
                r"GB3	CR	×	LF",
                r"GB4	(Control | CR | LF)	÷	 ",
                r"GB5		÷	(Control | CR | LF)",
                # Do not break Hangul syllable or other conjoining sequences.
                r"GB6	L	×	(L | V | LV | LVT)",
                r"GB7	(LV | V)	×	(V | T)",
                r"GB8	(LVT | T)	×	T",
                # Do not break before extending characters or ZWJ.
                r"GB9	 	×	(Extend | ZWJ)",
                # The GB9a and GB9b rules only apply to extended grapheme clusters:
                # Do not break before SpacingMarks, or after Prepend characters.
                r"GB9a	 	×	SpacingMark",
                r"GB9b	Prepend	×	 ",
                # The GB9c rule only applies to extended grapheme clusters:
                # Do not break within certain combinations with Indic_Conjunct_Break (InCB)=Linker.
                r"GB9c	\p{InCB=Consonant} [ \p{InCB=Extend} \p{InCB=Linker} ]* \p{InCB=Linker} [ \p{InCB=Extend} \p{InCB=Linker} ]*	×	\p{InCB=Consonant}",
                # Do not break within emoji modifier sequences or emoji zwj sequences.
                r"GB11	\p{Extended_Pictographic} Extend* ZWJ	×	\p{Extended_Pictographic}",
                # Do not break within emoji flag sequences. That is, do not break between regional indicator (RI) symbols if there is an odd number of RI characters before the break point.
                r"GB12	sot (RI RI)* RI	×	RI",
                r"GB13	[^RI] (RI RI)* RI	×	RI",
                # Otherwise, break everywhere.
                r"GB999	Any	÷	Any",
            ],
        ).build()
    )

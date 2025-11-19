from typing import Any, cast
import pytest
from unicode_segment._rule_parser import (
    RuleParser,
    GroupToken,
    CharClassToken,
    IdentToken,
    OtherToken,
)
from textwrap import dedent


class TestTokenizePart:
    """Test the tokenize_part method of RuleParser."""

    @pytest.fixture
    def parser(self):
        """Create a RuleParser instance for testing."""
        return RuleParser(prop_name="test", macros={}, rules=[])

    def test_basic_sanity_checks(self):
        config = RuleParser(
            "XX",
            {},
            [
                r"XX1	sot	×	Any",
                r"XX999	Any	÷	Any",
            ],
        ).build()

        assert config.break_rules == {"XX999"}
        # Has Any-Any break rule, so no break candidates pattern (all positions are possible breaks)
        assert config.break_candidates_pattern is None

        config = RuleParser(
            "YY",
            {},
            [
                r"YY1	sot	÷	Any",
                r"YY999	Any	×	Any",
            ],
        ).build()

        assert config.break_rules == {"YY1"}
        # No Any-Any break rule, so break candidates pattern exists
        assert config.break_candidates_pattern is not None

    def test_simple_identifier(self, parser: RuleParser):
        """Test tokenizing a simple identifier."""
        tokens = parser.tokenize_part("foo")
        assert len(tokens) == 1
        assert isinstance(tokens[0], IdentToken)
        assert tokens[0].value == "foo"

    def test_multiple_identifiers_with_whitespace(self, parser: RuleParser):
        """Test tokenizing multiple identifiers separated by whitespace."""
        tokens = parser.tokenize_part("foo bar")
        assert len(tokens) == 2
        assert isinstance(tokens[0], IdentToken)
        assert tokens[0].value == "foo"
        assert isinstance(tokens[1], IdentToken)
        assert tokens[1].value == "bar"

    def test_simple_group(self, parser: RuleParser):
        """Test tokenizing a simple group."""
        tokens = parser.tokenize_part("(foo)")
        assert len(tokens) == 1
        assert isinstance(tokens[0], GroupToken)
        assert tokens[0].value == "(foo)"
        assert tokens[0].negated is False
        assert len(tokens[0].children) == 1
        assert isinstance(tokens[0].children[0], IdentToken)
        assert tokens[0].children[0].value == "foo"

    def test_group_with_multiple_items(self, parser: RuleParser):
        """Test tokenizing a group with multiple items."""
        tokens = parser.tokenize_part("(foo bar)")
        assert len(tokens) == 1
        assert isinstance(tokens[0], GroupToken)
        assert tokens[0].value == "(foo bar)"
        assert len(tokens[0].children) == 2
        assert isinstance(tokens[0].children[0], IdentToken)
        assert tokens[0].children[0].value == "foo"
        assert isinstance(tokens[0].children[1], IdentToken)
        assert tokens[0].children[1].value == "bar"

    def test_nested_groups(self, parser: RuleParser):
        """Test tokenizing nested groups."""
        tokens = parser.tokenize_part("(foo (bar))")
        assert len(tokens) == 1
        assert isinstance(tokens[0], GroupToken)
        assert tokens[0].value == "(foo (bar))"
        assert len(tokens[0].children) == 2
        assert isinstance(tokens[0].children[0], IdentToken)
        assert tokens[0].children[0].value == "foo"
        assert isinstance(tokens[0].children[1], GroupToken)
        assert tokens[0].children[1].value == "(bar)"
        assert len(tokens[0].children[1].children) == 1
        assert isinstance(tokens[0].children[1].children[0], IdentToken)
        assert tokens[0].children[1].children[0].value == "bar"

    def test_negated_group(self, parser: RuleParser):
        """Test tokenizing a negated group."""
        tokens = parser.tokenize_part("[^abc]")
        assert len(tokens) == 1
        assert isinstance(tokens[0], CharClassToken)
        assert tokens[0].value == "[^abc]"
        assert len(tokens[0].children) == 1
        assert isinstance(tokens[0].children[0], IdentToken)
        assert tokens[0].children[0].value == "abc"

    def test_negated_group_with_whitespace(self, parser: RuleParser):
        """Test tokenizing a negated group with whitespace."""
        tokens = parser.tokenize_part("[^ foo bar ]")
        assert len(tokens) == 1
        assert isinstance(tokens[0], CharClassToken)
        assert tokens[0].value == "[^ foo bar ]"
        # Inner content is "foo bar" after stripping [^ and ]
        assert len(tokens[0].children) == 2
        assert isinstance(tokens[0].children[0], IdentToken)
        assert tokens[0].children[0].value == "foo"
        assert isinstance(tokens[0].children[1], IdentToken)
        assert tokens[0].children[1].value == "bar"

    def test_multiple_groups_in_sequence(self, parser: RuleParser):
        """Test tokenizing multiple groups in sequence."""
        tokens = parser.tokenize_part("(foo)(bar)")
        assert len(tokens) == 2
        assert isinstance(tokens[0], GroupToken)
        assert tokens[0].value == "(foo)"
        assert isinstance(tokens[1], GroupToken)
        assert tokens[1].value == "(bar)"

    def test_identifier_followed_by_group(self, parser: RuleParser):
        """Test tokenizing identifier followed by group."""
        tokens = parser.tokenize_part("foo(bar)")
        assert len(tokens) == 2
        assert isinstance(tokens[0], IdentToken)
        assert tokens[0].value == "foo"
        assert isinstance(tokens[1], GroupToken)
        assert tokens[1].value == "(bar)"

    def test_empty_group(self, parser: RuleParser):
        """Test tokenizing an empty group."""
        tokens = parser.tokenize_part("()")
        assert len(tokens) == 1
        assert isinstance(tokens[0], GroupToken)
        assert tokens[0].value == "()"
        assert len(tokens[0].children) == 0

    def test_complex_nested_structure(self, parser: RuleParser):
        """Test tokenizing a complex nested structure."""
        tokens = parser.tokenize_part("foo (bar [^baz qux] X)")
        assert len(tokens) == 2
        assert isinstance(tokens[0], IdentToken)
        assert tokens[0].value == "foo"
        assert isinstance(tokens[1], GroupToken)
        assert tokens[1].value == "(bar [^baz qux] X)"

        # Check children of the group
        group_children = tokens[1].children
        assert len(group_children) == 3
        assert isinstance(group_children[0], IdentToken)
        assert group_children[0].value == "bar"
        assert isinstance(group_children[1], CharClassToken)
        assert group_children[1].value == "[^baz qux]"
        assert isinstance(group_children[2], IdentToken)
        assert group_children[2].value == "X"

    def test_other_token(self, parser: RuleParser):
        """Test tokenizing other characters."""
        tokens = parser.tokenize_part("+")
        assert len(tokens) == 1
        assert isinstance(tokens[0], OtherToken)
        assert tokens[0].value == "+"

    def test_mixed_content(self, parser: RuleParser):
        """Test tokenizing mixed content with various token types."""
        tokens = parser.tokenize_part("Any (CR LF)")
        assert len(tokens) == 2
        assert isinstance(tokens[0], IdentToken)
        assert tokens[0].value == "Any"
        assert isinstance(tokens[1], GroupToken)
        assert tokens[1].value == "(CR LF)"

    def test_deeply_nested_groups(self, parser: RuleParser):
        """Test tokenizing deeply nested groups."""
        tokens = parser.tokenize_part("(a (b (c)))")
        assert len(tokens) == 1
        assert isinstance(tokens[0], GroupToken)

        # First level
        assert len(tokens[0].children) == 2
        assert tokens[0].children[0].value == "a"
        assert isinstance(tokens[0].children[1], GroupToken)

        # Second level
        second_level = tokens[0].children[1]
        assert len(second_level.children) == 2
        assert second_level.children[0].value == "b"
        assert isinstance(second_level.children[1], GroupToken)

        # Third level
        third_level = second_level.children[1]
        assert len(third_level.children) == 1
        assert third_level.children[0].value == "c"

    def test_negated_group_in_group(self, parser: RuleParser):
        """Test tokenizing a negated group inside a regular group."""
        tokens = parser.tokenize_part("(foo [^bar])")
        assert len(tokens) == 1
        assert isinstance(tokens[0], GroupToken)
        assert len(tokens[0].children) == 2
        assert isinstance(tokens[0].children[0], IdentToken)
        assert tokens[0].children[0].value == "foo"
        assert isinstance(tokens[0].children[1], CharClassToken)
        assert tokens[0].children[1].value == "[^bar]"

    def test_negated_group_with_not_symbol(self, parser: RuleParser):
        """Test tokenizing a negated group with ¬ symbol."""
        tokens = parser.tokenize_part("¬(foo)")
        assert len(tokens) == 1
        assert isinstance(tokens[0], GroupToken)
        assert tokens[0].value == "¬(foo)"
        assert tokens[0].negated is True
        assert len(tokens[0].children) == 1
        assert isinstance(tokens[0].children[0], IdentToken)
        assert tokens[0].children[0].value == "foo"

    def test_negated_group_with_not_symbol_and_whitespace(self, parser: RuleParser):
        """Test tokenizing a negated group with ¬ and whitespace."""
        tokens = parser.tokenize_part("¬ (foo bar)")
        assert len(tokens) == 1
        assert isinstance(tokens[0], GroupToken)
        assert tokens[0].value == "¬ (foo bar)"
        assert tokens[0].negated is True
        assert len(tokens[0].children) == 2
        assert tokens[0].children[0].value == "foo"
        assert tokens[0].children[1].value == "bar"

    def test_negated_char_class(self, parser: RuleParser):
        """Test tokenizing a negated char class with [^...]."""
        tokens = parser.tokenize_part("[^abc]")
        assert len(tokens) == 1
        assert isinstance(tokens[0], CharClassToken)
        assert tokens[0].value == "[^abc]"
        assert tokens[0].negated is True
        assert len(tokens[0].children) == 1
        assert tokens[0].children[0].value == "abc"

    def test_non_negated_char_class(self, parser: RuleParser):
        """Test tokenizing a non-negated char class with [...]."""
        tokens = parser.tokenize_part("[abc]")
        assert len(tokens) == 1
        assert isinstance(tokens[0], CharClassToken)
        assert tokens[0].value == "[abc]"
        assert tokens[0].negated is False
        assert len(tokens[0].children) == 1
        assert tokens[0].children[0].value == "abc"

    def test_negated_group_in_negated_char_class(self, parser: RuleParser):
        """Test tokenizing a negated group inside a negated char class."""
        tokens = parser.tokenize_part("[^foo ¬(bar)]")
        assert len(tokens) == 1
        assert isinstance(tokens[0], CharClassToken)
        assert tokens[0].negated is True
        assert len(tokens[0].children) == 2
        assert tokens[0].children[0].value == "foo"
        assert isinstance(tokens[0].children[1], GroupToken)
        assert tokens[0].children[1].negated is True
        assert tokens[0].children[1].value == "¬(bar)"

    def test_complex_negation_nesting(self, parser: RuleParser):
        """Test complex nesting with multiple negations."""
        tokens = parser.tokenize_part("¬(foo [^bar] ¬(baz))")
        assert len(tokens) == 1
        assert isinstance(tokens[0], GroupToken)
        assert tokens[0].negated is True

        children = tokens[0].children
        assert len(children) == 3
        assert children[0].value == "foo"
        assert isinstance(children[1], CharClassToken)
        assert children[1].negated is True
        assert isinstance(children[2], GroupToken)
        assert children[2].negated is True
        assert children[2].value == "¬(baz)"


class TestGetRule:
    """Test the get_rule and related methods of RuleParser."""

    @pytest.fixture
    def parser(self):
        """Create a RuleParser instance with some macros for testing."""
        macros = {
            "Control": {"Cc", "Cf"},
            "Extend": {"Me", "Mn"},
        }
        return RuleParser(prop_name="Grapheme_Cluster_Break", macros=macros, rules=[])

    def test_simple_break_rule(self, parser: RuleParser):
        """Test a simple break rule."""
        parts = {"name": "GB999", "lhs": "Any", "rhs": "Any", "operator": "÷"}
        is_break, name, (lhs, rhs) = parser.get_rule(parts)

        assert is_break is True
        assert name == "GB999"
        assert "(?<=" in lhs
        assert "(?=" in rhs
        assert "." in lhs  # Any maps to .
        assert "." in rhs

    def test_simple_no_break_rule(self, parser: RuleParser):
        """Test a simple no-break rule."""
        parts = {"name": "GB3", "lhs": "CR", "rhs": "LF", "operator": "×"}
        is_break, name, (lhs, rhs) = parser.get_rule(parts)

        assert is_break is False
        assert name == "GB3"
        assert "(?<=" in lhs
        assert "(?=" in rhs
        assert "Grapheme_Cluster_Break=CR" in lhs
        assert "Grapheme_Cluster_Break=LF" in rhs

    def test_rule_with_macro(self, parser: RuleParser):
        """Test rule using a macro."""
        parts = {"name": "GB9", "lhs": None, "rhs": "Extend", "operator": "×"}
        is_break, name, (lhs, rhs) = parser.get_rule(cast(Any, parts))

        assert is_break is False
        assert name == "GB9"
        assert lhs == ""
        assert "(?=" in rhs
        # Macro should expand to character class
        assert "[" in rhs
        assert "Grapheme_Cluster_Break=Me" in rhs
        assert "Grapheme_Cluster_Break=Mn" in rhs

    def test_rule_with_group(self, parser: RuleParser):
        """Test rule with grouped elements."""
        parts = {"name": "GB11", "lhs": None, "rhs": "(LF | CR)", "operator": "÷"}
        is_break, name, (lhs, rhs) = parser.get_rule(cast(Any, parts))

        assert is_break is True
        assert name == "GB11"
        assert lhs == ""
        assert "(?=" in rhs
        assert "(?:" in rhs  # Non-capturing group

    def test_rule_with_negated_group(self, parser: RuleParser):
        """Test rule with negated group alternation."""
        parts = {"name": "TestNeg", "lhs": "Any", "rhs": "¬(CR | LF)", "operator": "×"}
        is_break, name, (lhs, rhs) = parser.get_rule(parts)

        assert is_break is False
        assert name == "TestNeg"
        # Negated alternation groups like ¬(A | B) should generate [^AB] (negated char class)
        # In RHS (lookahead), this becomes (?=[^AB])
        assert "[^" in rhs  # Negated character class
        assert "(?=" in rhs  # Positive lookahead

    def test_rule_with_char_class(self, parser: RuleParser):
        """Test rule with character class."""
        parts = {"name": "TestCC", "lhs": "[CR LF]", "rhs": "Any", "operator": "÷"}
        is_break, name, (lhs, rhs) = parser.get_rule(parts)

        assert is_break is True
        assert name == "TestCC"
        assert "[" in lhs
        assert "Grapheme_Cluster_Break=CR" in lhs
        assert "Grapheme_Cluster_Break=LF" in lhs

    def test_rule_with_negated_char_class(self, parser: RuleParser):
        """Test rule with negated character class."""
        parts = {"name": "TestNCC", "lhs": "Any", "rhs": "[^Control]", "operator": "×"}
        is_break, name, (lhs, rhs) = parser.get_rule(parts)

        assert is_break is False
        assert name == "TestNCC"
        assert "[^" in rhs
        assert "Grapheme_Cluster_Break=Cc" in rhs
        assert "Grapheme_Cluster_Break=Cf" in rhs

    def test_skip_rule(self, parser: RuleParser):
        """Test skip rule (→ operator)."""
        parts = {"name": "GB9c", "lhs": "X* Extend", "rhs": None, "operator": "→"}
        parser.skip = None  # Reset skip
        is_break, name, (lhs, rhs) = parser.get_rule(cast(Any, parts))

        assert is_break is False
        assert name == "GB9c"
        assert lhs == ""
        assert "(?=" in rhs
        # Skip should be set after processing
        assert parser.skip is not None

    def test_special_ident_sot(self, parser: RuleParser):
        """Test start-of-text special identifier."""
        parts = {"name": "GB1", "lhs": "sot", "rhs": "Any", "operator": "÷"}
        is_break, name, (lhs, rhs) = parser.get_rule(parts)

        assert is_break is True
        assert "(?<!.)" in lhs  # sot maps to negative lookbehind

    def test_special_ident_eot(self, parser: RuleParser):
        """Test end-of-text special identifier."""
        parts = {"name": "GB2", "lhs": "Any", "rhs": "eot", "operator": "÷"}
        is_break, name, (lhs, rhs) = parser.get_rule(parts)

        assert is_break is True
        assert "(?!.)" in rhs  # eot maps to negative lookahead

    def test_get_rules(self, parser: RuleParser):
        """Test cooking multiple parts."""
        parts_list = [
            {"name": "Rule1", "lhs": "CR", "rhs": "LF", "operator": "×"},
            {"name": "Rule2", "lhs": "Any", "rhs": "Any", "operator": "÷"},
        ]

        rules = parser.get_rules(parts_list)

        assert len(rules) == 2
        assert rules[0][0] is False  # No-break
        assert rules[0][1] == "Rule1"
        assert rules[1][0] is True  # Break
        assert rules[1][1] == "Rule2"

    def test_complex_nested_rule(self, parser: RuleParser):
        """Test a complex rule with nested groups and char classes."""
        parts = {
            "name": "Complex",
            "lhs": "¬([^Control] (CR | LF))",
            "rhs": "Extend",
            "operator": "×",
        }
        is_break, name, (lhs, rhs) = parser.get_rule(parts)

        assert is_break is False
        assert name == "Complex"
        # Should have negated group in lhs
        assert "(?!" in lhs
        # Should have negated char class inside
        assert "[^" in lhs

    def test_escapes(self, parser: RuleParser):
        tokens = parser.tokenize_part(r"(\p{X}|[\p{Y}\p{Z}])")
        assert parser.serialize_tokens(tokens) == dedent(
            r"""
            GroupToken: '(\\p{X}|[\\p{Y}\\p{Z}])'
                OtherToken: '\\p{X}'
                OtherToken: '|'
                CharClassToken: '[\\p{Y}\\p{Z}]'
                    OtherToken: '\\p{Y}'
                    OtherToken: '\\p{Z}'
            """
        )

    def test_escapes_with_ws(self, parser: RuleParser):
        tokens = parser.tokenize_part(r"( \p{X} | [ \p{Y} \p{Z} ] )")
        assert parser.serialize_tokens(tokens) == dedent(
            r"""
            GroupToken: '( \\p{X} | [ \\p{Y} \\p{Z} ] )'
                OtherToken: '\\p{X}'
                OtherToken: '|'
                CharClassToken: '[ \\p{Y} \\p{Z} ]'
                    OtherToken: '\\p{Y}'
                    OtherToken: '\\p{Z}'
            """
        )

    def test_serialize_tokens(self, parser: RuleParser):
        tokens = parser.tokenize_part("¬(foo [^bar baz] qux)")
        assert parser.serialize_tokens(tokens) == dedent(
            """
            GroupToken (negated): '¬(foo [^bar baz] qux)'
                IdentToken: 'foo'
                CharClassToken (negated): '[^bar baz]'
                    IdentToken: 'bar'
                    IdentToken: 'baz'
                IdentToken: 'qux'
            """
        )

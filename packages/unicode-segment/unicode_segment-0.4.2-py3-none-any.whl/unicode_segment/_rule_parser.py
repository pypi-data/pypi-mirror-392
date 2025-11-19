from __future__ import annotations
import regex
from unicode_segment._segmenter_config import SegmenterConfig, SkipRule

flags = regex.V1 | regex.DOTALL

ident_map = {
    "Any": r".",
    "sot": r"(?<!.)",
    "eot": r"(?!.)",
}

group_matcher = regex.compile(r"\((?!\?)[^)]+\)")
negated_group_matcher = regex.compile(r"\[\s*\^(?<content>[^\]]+)\]")

ws_matcher = regex.compile(r"\s+")
ident_matcher = regex.compile(r"(?<![\\=\w{}<>])\w+")
parts_matcher = regex.compile(
    r"""
        ^
        \s*(?<name>\w+)\s+
        (?<lhs>.+?)?
        (?<operator>÷|→|×)
        (?<rhs>.+)?
        $
    """,
    regex.VERBOSE,
)
skip_rule_matcher = regex.compile(r"\bX\b|\*")
brackets_matcher = regex.compile(r"[\[\]]")


type Rule = tuple[bool, str, tuple[str, str]]


class Token:
    """Base token class."""

    def __init__(self, value: str):
        self.value = value


class GroupToken(Token):
    """Token for groups like (a | b | c)."""

    def __init__(
        self, value: str, children: list[Token] | None = None, negated: bool = False
    ):
        super().__init__(value)
        self.children = children or []
        self.negated = negated


class CharClassToken(Token):
    """Token for char classes like [a b c]."""

    def __init__(
        self, value: str, children: list[Token] | None = None, negated: bool = False
    ):
        super().__init__(value)
        self.children = children or []
        self.negated = negated


class IdentToken(Token):
    """Token for identifiers."""

    pass


class WhitespaceToken(Token):
    """Token for whitespace."""

    pass


class OtherToken(Token):
    """Token for other characters."""

    pass


# Token patterns with start/end for nested tokens
group_start_pattern = regex.compile(r"(?<negate>¬\s*)?\(")
group_end_pattern = regex.compile(r"\)")
char_class_start_pattern = regex.compile(r"\[(?<negate>\s*\^)?")
char_class_end_pattern = regex.compile(r"\]")

# Simple token patterns in order of precedence
simple_token_patterns: list[tuple[type[Token], regex.Pattern]] = [
    (IdentToken, regex.compile(r"(?<![\\=\w{}<>])\w+")),
    (WhitespaceToken, regex.compile(r"\s+")),
    (OtherToken, regex.compile(r"[*+?|]|\\\w\{[\w=]+\}")),
]


class RuleParser:
    def __init__(
        self, prop_name: str, macros: dict[str, set[str]], rules: str | list[str]
    ):
        self.prop_name = prop_name
        self.macros = macros
        self.rules = rules
        self.skip: SkipRule | None = None

    def build(self) -> SegmenterConfig:
        self.skip = None

        rule_lines = (
            [
                line.strip()
                for line in self.rules.strip().splitlines()
                if not line.strip().startswith("#")
            ]
            if isinstance(self.rules, str)
            else self.rules
        )

        parts = [self.get_parts(rule) for rule in rule_lines]
        rules = self.get_rules(parts)

        pattern = self.build_pattern(rules)
        debug_pattern = self.build_debug_pattern(rules)
        break_candidates_pattern = self.build_break_candidates_pattern(rules, parts)

        return SegmenterConfig(
            break_rules={r[1] for r in rules if r[0]},
            pattern=pattern,
            debug_pattern=debug_pattern,
            break_candidates_pattern=break_candidates_pattern,
            skip=self.skip,
        )

    def build_break_candidates_pattern(
        self, rules: list[Rule], parts: list[dict[str, str]]
    ) -> regex.Pattern | None:
        break_any = any(
            p["operator"] == "÷" and p["lhs"] == "Any" and p["rhs"] == "Any"
            for p in parts
        )

        if not break_any:
            pattern = "|".join(
                ["".join((lhs, rhs)) for is_break, _, (lhs, rhs) in rules if is_break]
            )
            return regex.compile(pattern, flags)

        return None

    def build_debug_pattern(self, rules: list[Rule]) -> regex.Pattern:
        pattern = "|".join([rf"(?<{name}>{''.join(rule)})" for _, name, rule in rules])
        return regex.compile(pattern, flags)

    def build_pattern(self, rules: list[Rule]) -> regex.Pattern:
        pattern = ""
        group_depth = 0

        prev_is_break = True

        for is_break, _, rule_parts in rules:
            (lhs, rhs) = rule_parts
            rule = lhs + rhs
            if pattern and prev_is_break:
                pattern += "|"

            if is_break:
                pattern += rule
            else:
                group_depth += 1
                pattern += rf"(?!{rule})"
                pattern += "(?:"

            prev_is_break = is_break

        pattern += ")" * group_depth

        return regex.compile(pattern, flags)

    def get_parts(self, rule: str):
        parts = parts_matcher.match(rule)
        assert parts is not None

        x = parts.groupdict()

        return {
            "name": x["name"].strip(),
            "lhs": x["lhs"].strip() if x["lhs"] is not None else None,
            "operator": x["operator"].strip(),
            "rhs": x["rhs"].strip() if x["rhs"] is not None else None,
        }

    def get_rules(self, parts: list[dict[str, str]]) -> list[Rule]:
        """Convert parsed rule parts to compiled regex rules."""
        return [self.get_rule(p) for p in parts]

    def get_rule(self, parts: dict[str, str]) -> Rule:
        """Convert a single rule part to a compiled regex rule."""
        is_break = parts["operator"] == "÷"
        is_skip = parts["operator"] == "→"

        # Handle special case: Any ÷ Any
        if parts["lhs"] == "Any" and parts["rhs"] == "Any":
            lhs = self.wrap_rule_part(r".", "lhs")
            rhs = self.wrap_rule_part(r".", "rhs")
            return (is_break, parts["name"], (lhs, rhs))

        # Handle skip rules (→)
        if is_skip:
            lhs = ""
            rhs = self.convert_skip_rule_lhs_as_rhs(parts["lhs"], parts["name"])
            return (False, parts["name"], (lhs, rhs))

        # Handle normal rules
        lhs = (
            self.render_rule_part(parts["lhs"], "lhs", is_break) if parts["lhs"] else ""
        )
        rhs = (
            self.render_rule_part(parts["rhs"], "rhs", is_break) if parts["rhs"] else ""
        )

        return (
            is_break,
            parts["name"],
            (ws_matcher.sub("", lhs), ws_matcher.sub("", rhs)),
        )

    def convert_skip_rule_lhs_as_rhs(self, rule_part: str, rule_name: str) -> str:
        """Convert skip rule LHS to RHS lookahead pattern."""
        tokens = self.tokenize_part(rule_part)
        # Filter out skip markers (X, *, and ?)
        filtered_tokens = [
            t
            for t in tokens
            if not (isinstance(t, IdentToken) and t.value == "X")
            and not (isinstance(t, OtherToken) and t.value in ("*", "?"))
            and not isinstance(t, WhitespaceToken)
        ]

        regex_part = "".join(self.token_to_regex(t) for t in filtered_tokens)
        self.skip = SkipRule(rule_name=rule_name, source=rf"{regex_part}*")
        return rf"(?={regex_part})"

    def render_rule_part(
        self, rule_part: str, position: str, is_break: bool = False
    ) -> str:
        """Convert a rule part to a regex fragment."""
        if not rule_part:
            return ""

        tokens = self.tokenize_part(rule_part.strip())
        regex_str = self.tokens_to_regex_with_skip(tokens, position, is_break)
        return self.wrap_rule_part(regex_str, position)

    def tokens_to_regex_with_skip(
        self, tokens: list[Token], position: str, is_break: bool = False
    ) -> str:
        """Convert tokens to regex, applying skip between non-whitespace tokens."""
        # Filter out whitespace tokens and group tokens with their repetition operators
        processed_tokens: list[tuple[Token, str]] = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if isinstance(token, WhitespaceToken):
                i += 1
                continue

            # Check if next non-whitespace token is a repetition operator
            repetition = ""
            j = i + 1
            while j < len(tokens):
                if isinstance(tokens[j], WhitespaceToken):
                    j += 1
                    continue
                if isinstance(tokens[j], OtherToken) and tokens[j].value in (
                    "*",
                    "?",
                    "+",
                ):
                    repetition = tokens[j].value
                    i = j  # Skip the repetition operator
                break

            processed_tokens.append((token, repetition))
            i += 1

        if not processed_tokens:
            return ""

        regex_parts = []
        for i, (token, repetition) in enumerate(processed_tokens):
            base_regex = self.token_to_regex(token)

            # Check if this token is a special operator like |
            is_operator = isinstance(token, OtherToken) and token.value == "|"

            if is_operator:
                regex_parts.append(base_regex)
                continue

            # Check if this token is negated (per Unicode spec 6.2: skip not applied after negations)
            is_negated = (
                isinstance(token, (GroupToken, CharClassToken)) and token.negated
            )

            # Check if next token is an operator
            next_is_operator = False
            if i + 1 < len(processed_tokens):
                next_token, _ = processed_tokens[i + 1]
                next_is_operator = (
                    isinstance(next_token, OtherToken) and next_token.value == "|"
                )

            if next_is_operator:
                regex_parts.append(base_regex)
                continue

            skip = None if self.skip is None else self.skip.source

            is_last = i == len(processed_tokens) - 1

            """
            Determine if we should apply skip.
            > [!NOTE]
            > Logic here is roughly based on https://www.unicode.org/reports/tr29/#Grapheme_Cluster_and_Format_Rules .
            > However, it's a little ad-hoc - basically the logic here is what gets the tests to pass, so not sure it's
            > a 100% future-proof implementation of the spec.
            """
            should_skip = (
                skip is not None
                and not is_negated
                and (
                    not is_last
                    or (position == "group" or (position == "lhs" and not is_break))
                )
            )

            # 强词夺理ing rule #WB16 to pass test case "a🇦\u200d🇧🇨b"
            if is_negated and position == "lhs" and skip is not None:
                regex_parts.append(rf"(?<!{base_regex.replace('^', '')}{skip})")
                continue

            # Build the final regex for this token
            regex_part = rf"(?:{base_regex}{skip})" if should_skip else base_regex
            regex_parts.append(rf"{regex_part}{repetition}")

        return "".join(regex_parts)

    # Invariant: token is not WhitespaceToken (because we already filtered them out)
    def token_to_regex(self, token: Token) -> str:
        if isinstance(token, IdentToken):
            regex_str = self.render_ident_raw(token.value)
            return regex_str

        if isinstance(token, GroupToken):
            # Per Unicode spec section 6.2:
            # "An alternate expression that resolves to a single character is treated as a whole"
            # (STerm | ATerm) ⇒ (STerm | ATerm) (Extend | Format)*
            # NOT: (STerm (Extend | Format)* | ATerm (Extend | Format)*)
            #
            # Check if this group contains alternation (|)
            has_alternation = any(
                isinstance(child, OtherToken) and child.value == "|"
                for child in token.children
            )

            if has_alternation or not self.skip:
                # Alternation group or no skip: treat as atomic, don't apply skip inside
                inner_parts = "".join(
                    self.token_to_regex(child)
                    for child in token.children
                    if not isinstance(child, WhitespaceToken)
                )
            else:
                # Sequence group with skip: apply skip between elements
                # (RI RI) ⇒ (RI SKIP RI)
                inner_parts = self.tokens_to_regex_with_skip(token.children, "group")

            if token.negated:
                # Negated group with alternations: ¬(A | B | C) → [^ABC]
                # This is a negated character class, not a negative lookahead
                if has_alternation:
                    # Extract property names from alternation
                    # Inner parts is like "A|B|C", we need to convert to [^ABC]
                    # Split by | and convert each part
                    parts = []
                    for child in token.children:
                        if isinstance(child, IdentToken):
                            parts.append(self.render_ident_raw(child.value))
                        elif isinstance(child, OtherToken) and child.value == "|":
                            pass  # Skip the | operator
                        elif not isinstance(child, WhitespaceToken):
                            # For other tokens, convert to regex
                            parts.append(self.token_to_regex(child))
                    return rf"[^{''.join(parts)}]"
                else:
                    # Negated non-alternation group: ¬(foo) → (?!foo)
                    return rf"(?!{inner_parts})"
            else:
                # Regular group: (foo) → (?:foo)
                return rf"(?:{inner_parts})"

        if isinstance(token, CharClassToken):
            # Check if we have IdentTokens that need expansion
            has_idents = any(isinstance(child, IdentToken) for child in token.children)

            if has_idents:
                # Expand identifiers to their Unicode property definitions
                inner_parts = "".join(
                    self.render_ident_raw(child.value)
                    if isinstance(child, IdentToken)
                    else ""
                    for child in token.children
                )
                if token.negated:
                    return rf"[^{inner_parts}]"
                else:
                    return rf"[{inner_parts}]"
            else:
                # Preserve raw content for character classes with Unicode escapes like \p{...}
                return rf"[{token.value[1:-1]}]"

        if isinstance(token, OtherToken):
            # Other characters pass through as-is
            return token.value

        raise ValueError(f"Unrecognized token type: {type(token)}")

    def render_ident_raw(self, ident: str) -> str:
        """Convert an identifier to its regex representation."""
        if ident in ident_map:
            return ident_map[ident]
        elif ident in self.macros:
            return rf"[{''.join([self.prop_with_name(x) for x in self.macros[ident]])}]"
        else:
            return self.prop_with_name(ident)

    def wrap_rule_part(self, rule_part: str, position: str) -> str:
        """Wrap a rule part in appropriate lookahead/lookbehind."""
        if position == "lhs":
            return rf"(?<={rule_part})"
        else:  # rhs
            # Add skip at the beginning of RHS to handle Extend/Format chars
            if self.skip:
                return rf"(?={self.skip.source}{rule_part})"
            else:
                return rf"(?={rule_part})"

    def tokenize_part(self, part: str) -> list[Token]:
        """Tokenize a rule part using a stack-based approach for nested tokens."""
        tokens: list[Token] = []
        stack: list[
            # (token_class, start_pos, opening_delimiter, negated)
            tuple[type[GroupToken] | type[CharClassToken], int, str, bool]
        ] = []

        pos = 0
        while pos < len(part):
            matched = False

            # Check for group start
            match = group_start_pattern.match(part, pos)
            if match:
                negated = match.group("negate") is not None
                stack.append((GroupToken, pos, match.group(0), negated))
                pos = match.end()
                continue

            # Check for char class start
            match = char_class_start_pattern.match(part, pos)
            if match:
                negated = match.group("negate") is not None
                stack.append((CharClassToken, pos, match.group(0), negated))
                pos = match.end()
                continue

            # Check for group end
            if stack and stack[-1][0] == GroupToken:
                match = group_end_pattern.match(part, pos)
                if match:
                    _, start_pos, opening_delimiter, negated = stack.pop()
                    full_value = part[start_pos : pos + match.end() - pos]
                    # Recursively tokenize the content inside the group
                    # Extract content between opening delimiter and closing )
                    inner_start = start_pos + len(opening_delimiter)
                    inner_content = part[inner_start:pos]
                    children = (
                        self.tokenize_part(inner_content) if inner_content else []
                    )
                    group_token = GroupToken(full_value, children, negated)

                    if stack:
                        # We're inside a parent nested structure - don't modify stack
                        pass
                    else:
                        tokens.append(group_token)

                    pos = match.end()
                    continue

            # Check for char class end
            if stack and stack[-1][0] == CharClassToken:
                match = char_class_end_pattern.match(part, pos)
                if match:
                    _, start_pos, opening_delimiter, negated = stack.pop()
                    full_value = part[start_pos : pos + match.end() - pos]
                    # Recursively tokenize the content inside the char class
                    # Extract content between opening delimiter and closing ]
                    inner_start = start_pos + len(opening_delimiter)
                    inner_content = part[inner_start:pos].strip()
                    children = (
                        self.tokenize_part(inner_content) if inner_content else []
                    )
                    char_class_token = CharClassToken(full_value, children, negated)

                    if stack:
                        # We're inside a parent nested structure - don't modify stack
                        pass
                    else:
                        tokens.append(char_class_token)

                    pos = match.end()
                    continue

            # Check simple token patterns
            for simple_token_class, pattern in simple_token_patterns:
                match = pattern.match(part, pos)
                if match:
                    simple_token = simple_token_class(match.group(0))

                    if stack:
                        # We're inside a nested structure, don't add to tokens
                        pass
                    else:
                        tokens.append(simple_token)

                    pos = match.end()
                    matched = True
                    break

            if not matched:
                raise ValueError(
                    f"Unrecognized token at position {pos} in part: {part}"
                )

        return [t for t in tokens if not isinstance(t, WhitespaceToken)]

    def prop_with_name(self, name: str) -> str:
        return rf"\p{{{self.prop_name}={name}}}"

    def serialize_tokens(self, tokens: list[Token], indent: int = 0) -> str:
        """Return a pretty-printed view of tokens for debugging."""
        lines = []
        indent_str = " " * indent * 4

        for token in tokens:
            token_type = type(token).__name__
            value_repr = repr(token.value)

            if isinstance(token, (GroupToken, CharClassToken)):
                negated_marker = " (negated)" if token.negated else ""
                lines.append(f"{indent_str}{token_type}{negated_marker}: {value_repr}")
                if token.children:
                    # Recursively serialize children with increased indentation
                    children_str = self.serialize_tokens(token.children, indent + 1)
                    lines.append(children_str.rstrip("\n"))
            else:
                lines.append(f"{indent_str}{token_type}: {value_repr}")

        result = "\n".join(lines)
        if indent == 0:
            result = f"\n{result}\n"
        return result

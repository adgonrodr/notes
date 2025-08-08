import re

# Product name with a trailing version, e.g. "Test - dp - v1.0.1"
# Strict spacing: requires exactly " - " before the version and no extra spaces anywhere.
_PRODUCT_RE = re.compile(
    r"""
    ^
    (?P<name>\S(?:.*\S)?)      # <name>: at least one non-space; no leading/trailing space
                               # inside <name> (internal spaces allowed). Greedy so we
                               # capture everything up to the final " - vX.Y.Z".

    \s-\s                      # EXACT one space, a single '-', and one space (i.e., " - ")

    [vV]?                      # optional 'v' or 'V' prefix

    (?P<maj>0|[1-9]\d*)        # MAJOR: integer; no leading zeros unless it's "0"
    \.
    (?P<min>0|[1-9]\d*)        # MINOR: same rule
    \.
    (?P<patch>0|[1-9]\d*)      # PATCH: same rule

    $                          # end: no trailing spaces allowed
    """,
    re.VERBOSE,
)

# Bare version like "v1.2.3" or "1.2.3"
# Strict: no leading/trailing spaces.
_VERSION_RE = re.compile(
    r"""
    ^
    [vV]?                      # optional 'v' or 'V'
    (?P<maj>0|[1-9]\d*)        # MAJOR
    \.
    (?P<min>0|[1-9]\d*)        # MINOR
    \.
    (?P<patch>0|[1-9]\d*)      # PATCH
    $                          # no extra spaces allowed
    """,
    re.VERBOSE,
)

def is_valid_product_name(s: str) -> bool:
    """
    Return True iff `s` matches '<name> - vMAJOR.MINOR.PATCH' with strict spacing.

    Rules enforced:
      - No leading/trailing whitespace on the whole string.
      - The separator before the version is EXACTLY " - ".
      - Optional 'v' or 'V' before the numeric version.
      - MAJOR/MINOR/PATCH are non-negative integers without leading zeros (except "0").
      - The version must be the last thing in the string.

    Note: The <name> can include additional ' - ' segments (e.g., "Test - dp - v1.0.1").
    This regex does not police the spacing of hyphens INSIDE <name>; it only enforces
    the spacing for the final separator before the version.
    """
    return bool(_PRODUCT_RE.fullmatch(s))


def higher_version(a: str, b: str) -> str:
    """
    Return whichever input string has the higher version (ties -> return `a`).

    Inputs can be:
      - A bare version: 'vMAJOR.MINOR.PATCH' or 'MAJOR.MINOR.PATCH' (no extra spaces).
      - A product name ending with a version: '<name> - vMAJOR.MINOR.PATCH'
        with EXACT separator " - " and no leading/trailing whitespace.

    Raises
    ------
    ValueError
        If a version cannot be parsed from either input under the strict rules.
    """
    def parse(s: str):
        m = _PRODUCT_RE.fullmatch(s) or _VERSION_RE.fullmatch(s)
        if not m:
            raise ValueError(
                f"Invalid version string: {s!r}. Expected either "
                "'vMAJOR.MINOR.PATCH' / 'MAJOR.MINOR.PATCH' (no spaces) or "
                "'<name> - vMAJOR.MINOR.PATCH' with EXACT ' - ' separator and no extra spaces."
            )
        return int(m["maj"]), int(m["min"]), int(m["patch"])

    va, vb = parse(a), parse(b)
    return a if va >= vb else b
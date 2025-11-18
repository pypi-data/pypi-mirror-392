"""Format specific load and dump implementations for the inverting pair mappings helper tool."""


def process(key: str, value: str, serial: int, marker: str, is_value: bool) -> tuple[str, str, bool]:
    """Process the key value pair and signal any marker as either key or value.

    If serial is 1 or greater, enter auto-serial mode.
    When in auto-serial mode and if marker is not empty, then inspect exemptions.
    If marker is_value, assume the marker is in the value slot of the incoming pair.
    """
    if serial:  # Use auto-serial on keys
        if marker:  # Signal any marker value to be kept as is and pause the auto increment
            if any([not is_value and key == marker, is_value and value == marker]):
                return key, value, True
        return str(serial), value, False
    return key, value, False


def nonjective(data: dict[str, str]) -> list[str]:
    """Assess the uniqueness of values, so we can invert without ambiguity."""
    if sorted(set(data.values())) == sorted(data.values()):
        return []

    pairs = {}
    for k, v in data.items():
        if v not in pairs:
            pairs[v] = [k]
        else:
            pairs[v].append(k)

    findings = []
    for value, keys in pairs.items():
        findings.append(f'{value=} occurs for {keys=}')

    return findings

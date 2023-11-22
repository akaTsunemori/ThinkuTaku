import re


def parse_line(line: str):
    """
    Parses a single input line.

    Args:
        line: The line to be parsed.

    Returns:
        The Tuple (rule, symptoms, probability).
    """
    cause = None
    symptoms = []
    probability = None
    # Clean string
    line = re.sub(' +', ' ', line)
    line = re.sub(' ,', ',', line)
    line = line.replace('“', '')
    line = line.replace('”', '')
    line = line.replace('"', '')
    # Parse cause
    pattern = r"([CS]\s+[\w\s]+\s+\d+)"
    match = re.search(pattern, line)
    if match:
        cause = match.group(1)
    # Parse symptoms
    pattern = r"([CS]\s+[\w\s]+\s+\d+),\s+(.*?),\s+(\d+\.\d+)"
    match = re.search(pattern, line)
    if match:
        symptoms = match.group(2)
    # Parse probability
    match = re.search(r"(\d+\.\d+)$", line)
    if match:
        probability = float(match.group(1))
    # Check if the input was parsed correctly
    if not (cause and symptoms and probability):
        raise Exception('Invalid input!')
    return cause, symptoms, probability


def parse_file(path):
    """
    Parses an input text file.

    Args:
        path: The path to the file.

    Returns:
        A List with the Tuples (rule, symptoms, probability).
    """
    with open(path, "r") as f:
        rules = []
        for line in f:
            rule, symptoms, probability = parse_line(line)
            rules.append((rule, symptoms, probability))
    return rules


def main():
    rules = parse_file("static/input.txt")
    for rule, symptoms, probability in rules:
        print("rule:", rule)
        print("symptoms:", symptoms)
        print("probability:", probability)


if __name__ == "__main__":
    main()

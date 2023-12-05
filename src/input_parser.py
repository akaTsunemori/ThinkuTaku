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
    line = re.sub(' +', ' ', line)
    line = re.sub(' ,', ',', line)
    line = line.replace('“', '')
    line = line.replace('”', '')
    line = line.replace('"', '')
    line = [
        line.split(',', 1)[0],
        line.split(',', 1)[1].rsplit(',', 1)[0],
        line.rsplit(',', 1)[1]]
    line = [i.strip() for i in line]
    cause, symptoms, probability = line
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
            symptoms = symptoms.strip(')')
            if symptoms.startswith('NOT ('):
                symptoms = symptoms.strip('NOT (')
                symptoms = symptoms.split(', ')
                for symptom in symptoms:
                    rules.append((rule, {symptom}, probability))
                continue
            symptoms = symptoms.strip('(')
            symptoms = symptoms.split('; ')
            symptoms = set(symptoms)
            probability = float(probability)
            rules.append((rule, symptoms, probability))
    return rules


def main():
    rules = parse_file("static/input.csv")
    for rule, symptoms, probability in rules:
        print("rule:", rule)
        print("symptoms:", symptoms)
        print("probability:", probability)


if __name__ == "__main__":
    main()

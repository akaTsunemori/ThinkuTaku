import re
import decision_tree

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
    symptoms = symptoms.replace("(","").replace(")","")
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

    # cria a raiz da arvore
    raiz = decision_tree.Node(is_leaf=False, name="raiz", probability=1)

    for rule, symptoms, probability in rules:
        
        print("----------------------------")
        print("rule:", rule)
        print("symptoms:", symptoms)
        print("probability:", probability)

    # vou escrever a arvore do exemplo logo nesse arquivo pois acho que faz mais sentido,
    # ao inves de escrever outro

        symptoms = symptoms.split(",")
        path_list = []
        print(symptoms)
        for sypmtom in symptoms:
            if sypmtom[0] == "N" or sypmtom[1] == "N":
                path_list.append(f"!{sypmtom[-1]}")
            else:
                path_list.append(sypmtom[-1])
        print(path_list)

    # pega os indices dos sintomas e regra
        rule_idx = rule[-1]
        path_list.append(rule_idx)
        print(path_list)
    
    # adiciona os caminhos a raiz da arvore
        raiz.insertNode(path_list=path_list, probability=probability, depth=1)

    


if __name__ == "__main__":
    main()

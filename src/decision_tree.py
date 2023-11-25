from queue import PriorityQueue


class Node:
    def __init__(self, data, probability = None) -> None:
        self.data = data
        self.probability = probability
        self.next = None
        self.children = set()

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, type(self)):
            return self.data == __value.data
        return self.data == __value

    def __str__(self) -> str:
        return self.data

    def __hash__(self) -> int:
        return hash(self.data)


class DecisionTree:
    symptoms = dict()
    priorities = dict()
    rules = None

    def __init__(self, rules) -> None:
        self.root = None
        DecisionTree.rules = rules

    def _build_dict(self):
        frequencies = dict()
        for rule, symptoms, _ in DecisionTree.rules:
            for symptom in symptoms:
                if not rule.startswith('C '):
                    continue
                if symptom not in frequencies:
                    frequencies[symptom] = 0
                frequencies[symptom] += 1
        DecisionTree.symptoms = frequencies

    def _gen_priorities(self):
        pq = PriorityQueue()
        symptoms = DecisionTree.symptoms
        pool_size = len(symptoms)
        for symptom in symptoms:
            ratio = symptoms[symptom] / pool_size
            ratio *= -1 # Convert the PQ into a Max PQ
            pq.put((ratio, symptom))
        while not pq.empty():
            ratio, symptom = pq.get()
            print(f'{(ratio * -100):.2f}% {symptom}')
            self.insert_node(symptom, self.root)

    def insert_node(self, data, root):
        if self.root is None:
            self.root = Node(data)
            return
        if root is None:
            return Node(data)
        if root.data != data:
            root.next = self.insert_node(data, root.next)
        return root

    def get_node_by_symptoms(self, symptoms, root):
        while root:
            if root.data in symptoms:
                return root
            root = root.next

    def sort_symptoms(self):
        new_rules = []
        priority = 0
        keys = list(DecisionTree.symptoms.keys())
        keys.sort(key=lambda a: (DecisionTree.symptoms[a], a))
        for k in keys:
            DecisionTree.priorities[k] = priority
            priority += 1
        for rule, symptoms, probability in DecisionTree.rules:
            symptoms = sorted(symptoms, reverse=True, key=lambda a: DecisionTree.priorities[a])
            new_rules.append((rule, symptoms, probability))
        DecisionTree.rules = new_rules

    def build_children(self, root: Node, visited: set = None, path: set = None):
        if not root:
            return
        if not visited:
            visited = set()
            visited.add(root.data)
        if not path:
            path = set()
            path.add(root.data)
        for rule, symptoms, probability in DecisionTree.rules:
            if len(path.intersection(symptoms)) != len(path):
                continue
            for symptom in symptoms:
                if symptom in visited:
                    continue
                if symptom in path:
                    continue
                child = Node(symptom)
                root.children.add(child)
                new_path = {i for i in path}
                new_path.add(symptom)
                if symptom != symptoms[-1]:
                    self.build_children(child, visited, new_path)
                break
        if root.next:
            visited.add(root.next.data)
            self.build_children(root.next, visited)

    def build_tree(self):
        root = self.root
        visited = set()
        while root:
            visited.add(root.data)
            self.build_children(root, visited)
            root = root.next

    def define_causes(self):
        for rule, symptoms, probability in DecisionTree.rules:
            node = self.get_node_by_symptoms(symptoms, self.root)
            symptoms_tmp = {i for i in symptoms if i != node.data}
            while symptoms_tmp:
                for child in node.children:
                    search = self.get_node_by_symptoms(symptoms_tmp, child)
                    if not search:
                        continue
                    if len(symptoms_tmp) > 1 and not search.children:
                        continue
                    node = search
                    symptoms_tmp.remove(node.data)
                    break
            node.children.add(Node(rule, probability=probability))

    def search(self, symptoms):
        node = self.get_node_by_symptoms(symptoms, self.root)
        symptoms_tmp = {i for i in symptoms if i != node.data}
        while symptoms_tmp:
            children = list(node.children)
            children.sort(reverse=True, key=lambda a: (DecisionTree.priorities[a.data], a.data))
            for child in children:
                if child.data in symptoms_tmp:
                    node = child
                    symptoms_tmp.remove(child.data)
                    break
        results = [i.data for i in node.children]
        return results


    def display(self, root, indent=0):
        if root:
            print('    ' * indent, end='')
            print(root.data + \
                  ':' * (root.probability is None) + ' ' + \
                  ('- ' + str(root.probability)) * (root.probability is not None),
                end=' ')
            print(*root.children, sep=', ')
            for child in root.children:
                self.display(child, indent+1)
            self.display(root.next)


rules_expanded = [
    ('C Naruto Uzumaki', {'Olhos azuis', 'Roupa laranja', 'Sapato azul', 'NOT Dor'}, 0.5),
    ('C Goku', {'Cabelo preto', 'Kimono laranja', 'Sapato azul'}, 0.7),
    ('C Monkey D. Luffy', {'Chapéu de palha', 'Camisa vermelha', 'Sapato azul'}, 0.6),
    ('C Ichigo Kurosaki', {'Cabelo laranja', 'Uniforme preto', 'Sapato marrom'}, 0.4),
    ('C Saitama', {'Careca', 'Roupa amarela', 'Sem expressão facial'}, 0.3),
    ('C Gon Freecss', {'Cabelo preto', 'Colete verde', 'Shorts pretos'}, 0.5),
    ('C Edward Elric', {'Cabelo loiro', 'Olhos azuis', 'Casaco vermelho', 'Automail'}, 0.6),
    ('C Sasuke Uchiha', {'Cabelo preto', 'Roupa preta', 'Sharingan'}, 0.7),
    ('C Vegeta', {'Cabelo preto', 'Armadura azul', 'Botas brancas'}, 0.6),
    ('C Light Yagami', {'Cabelo castanho', 'Camisa branca', 'Death Note'}, 0.4),
    ('C Makise Kurisu', {'Cabelo ruivo', 'Olhos azuis', 'Roupa branca', 'Sapato marrom'}, 0.2),
    ('C Nagisa Furukawa', {'Olhos azuis', 'Roupa marrom'}, 0.8),
    ('C Rei Ayanami', {'Olhos azuis', 'Roupa branca'}, 0.1),
    ('C Levi Ackerman', {'Olhos azuis', 'Roupa verde', 'Sapato preto'}, 0.2),
    ('C Haachama', {'CHAMACHAMA'}, 1.0)
]

tree = DecisionTree(rules=rules_expanded)
tree._build_dict()
tree._gen_priorities()
tree.sort_symptoms()
tree.build_tree()
tree.define_causes()
tree.display(tree.root)

print('\nDecisions with accurate symptoms:')
print('Chapéu de palha', 'Camisa vermelha', 'Sapato azul')
print(*tree.search({'Chapéu de palha', 'Camisa vermelha', 'Sapato azul'}))
print('Cabelo castanho', 'Camisa branca', 'Death Note')
print(*tree.search({'Cabelo castanho', 'Camisa branca', 'Death Note'}))
print('Olhos azuis', 'Roupa verde', 'Sapato preto')
print(*tree.search({'Olhos azuis', 'Roupa verde', 'Sapato preto'}))
print('Olhos azuis', 'Roupa marrom')
print(*tree.search({'Olhos azuis', 'Roupa marrom'}))
print('Cabelo ruivo', 'Olhos azuis', 'Roupa branca', 'Sapato marrom')
print(*tree.search({'Cabelo ruivo', 'Olhos azuis', 'Roupa branca', 'Sapato marrom'}))

print('\nDecisions with innacurate symptoms:')
print('(To-Do)')
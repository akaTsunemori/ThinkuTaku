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

    def __probability__(self):
        return self.probability

    def __hash__(self) -> int:
        return hash(self.data)
    
    def build_path(self, rule):

        if len(rule[1]) == 0:
            new_leaf = Node(rule[0], float(rule[2]))
            self.children.add(new_leaf)

        else:
            next_step = rule[1].pop()

            for child in self.children:
                if child.data == next_step:
                    child.build_path(rule)
                    return
                
            new_child = Node(data=next_step)
            self.children.add(new_child)
            new_child.build_path(rule)
    
    def find_path(self, symptoms, depth=1):

        if len(symptoms) == 0:

            for child in self.children:
                if child.probability:
                    print(f"{child.__str__()}: {child.__probability__()/depth}\n")
                else:
                    child.find_path(symptoms=symptoms, depth=depth+1)
            return
        
        for child in self.children:
            if child.data in symptoms:
                symptoms.remove(child.data)
                child.find_path(symptoms)
                print(child.data)
                return
        

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
                if symptom.startswith('NOT '):
                    symptom = symptom[4:]
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
            DecisionTree.priorities[symptom] = -100 * ratio
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



    def build_children(self, root):
        for rule in rules_expanded:
            most_commom = 0

            for sympton in rule[1]:
                if sympton.startswith('NOT '):
                    sympton = sympton[4:]
                cur_ocurrence = self.priorities[sympton]

                if most_commom < cur_ocurrence:
                    most_commom = cur_ocurrence
                    most_commom_name = sympton

            subTreeroot = self.get_node_by_symptoms(most_commom_name, root)
            rule[1].remove(most_commom_name)
            subTreeroot.build_path(rule)            
            

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
        for _ in range(len(symptoms_tmp)):
            for child in node.children:
                search = self.get_node_by_symptoms(symptoms_tmp, child)
                if search:
                    node = search
                    symptoms_tmp.remove(node.data)
                    break
        result = list(node.children)
        return result[0]

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

    def search_character(self, symptoms, root):
        most_commom = 0

        for symptom in symptoms:
            if symptom.startswith('NOT '):
                symptom = symptom[4:]
            cur_ocurrence = self.priorities[symptom]

            if most_commom < cur_ocurrence:
                most_commom = cur_ocurrence
                most_commom_name = symptom
        symptoms.remove(most_commom_name)
        subTreeroot = self.get_node_by_symptoms(most_commom_name, root)
        
        subTreeroot.find_path(symptoms)


rules_expanded = [
    ('C Naruto Uzumaki', {'Olhos azuis', 'Sapato azul', 'Roupa laranja', 'NOT Pain'}, 0.5),
    ('C Goku', {'Cabelo preto', 'Sapato azul', 'Kimono laranja'}, 0.7),
    ('C Monkey D. Luffy', {'Sapato azul', 'Chapéu de palha', 'Camisa vermelha'}, 0.6),
    ('C Ichigo Kurosaki', {'Sapato marrom', 'Cabelo laranja', 'Uniforme preto'}, 0.4),
    ('C Saitama', {'Careca', 'Roupa amarela', 'Sem expressão facial'}, 0.3),
    ('C Gon Freecss', {'Cabelo preto', 'Colete verde', 'Shorts pretos'}, 0.5),
    ('C Edward Elric', {'Olhos azuis', 'Cabelo loiro', 'Casaco vermelho', 'Automail'}, 0.6),
    ('C Sasuke Uchiha', {'Cabelo preto', 'Roupa preta', 'Sharingan'}, 0.7),
    ('C Vegeta', {'Cabelo preto', 'Armadura azul', 'Botas brancas'}, 0.6),
    ('C Light Yagami', {'Cabelo castanho', 'Camisa branca', 'Death Note'}, 0.4),
    ('C Makise Kurisu', {'Olhos azuis', 'Sapato marrom', 'Cabelo ruivo', 'Roupa branca'}, 0.2),
    ('C Nagisa Furukawa', {'Olhos azuis', 'Roupa marrom'}, 0.8),
    ('C Rei Ayanami', {'Olhos azuis', 'Roupa branca'}, 0.1),
    ('C Levi Ackerman', {'Olhos azuis', 'Sapato preto', 'Roupa verde'}, 0.2),
    ('C Franky', {'Roupa colorida', 'Sapato preto', 'Ser rei'}, 0.12),
    ('C Aurora', {'Olhos azuis', 'Sapato azul'}, 0.92),
    ('C Haachama', {'CHAMACHAMA'}, 1.0)
]


tree = DecisionTree(rules=rules_expanded)
tree._build_dict()
tree._gen_priorities()
tree.build_children(tree.root)
# tree.define_causes()
tree.display(tree.root)
tree.search_character({'Roupa colorida', 'Sapato preto', 'Ser rei'}, tree.root)

# print('\nDecisions with accurate symptoms:')
# print('Chapéu de palha', 'Camisa vermelha', 'Sapato azul')
# print(tree.search({'Chapéu de palha', 'Camisa vermelha', 'Sapato azul'}))
# print('Cabelo castanho', 'Camisa branca', 'Death Note')
# print(tree.search({'Cabelo castanho', 'Camisa branca', 'Death Note'}))
# print('Olhos azuis', 'Roupa verde', 'Sapato preto')
# print(tree.search({'Olhos azuis', 'Roupa verde', 'Sapato preto'}))
# print('\nDecisions with innacurate symptoms:')
# print('(To-Do)')
from queue import PriorityQueue


class Node:
    def __init__(self, data, probability = 0.0) -> None:
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
    __frequencies = dict()
    __priorities = dict()
    __causes = []
    __symptoms = []


    def __init__(self, rules) -> None:
        self.root = None
        for rule, symptoms, probability in rules:
            if rule.startswith('C '):
                DecisionTree.__causes.append((rule, symptoms, probability))
            elif rule.startswith('S '):
                DecisionTree.__symptoms.append((rule, symptoms, probability))
        self.__build_tree()

    def __compute_frequencies(self):
        '''
        Builds a dict counting the frequencies of the symptoms on the DecisionTree.__causes.

        Args:
            None

        Returns:
            None
        '''
        frequencies = dict()
        for rule, symptoms, _ in DecisionTree.__causes:
            for symptom in symptoms:
                if not rule.startswith('C '):
                    continue
                if symptom not in frequencies:
                    frequencies[symptom] = 0
                frequencies[symptom] += 1
        DecisionTree.__frequencies = frequencies

    def __ll_insert_node(self, data, root):
        '''
        Inserts a node on the Linked List.

        Args:
            data [str]: the data for the Node to be inserted.
            root [Node]: the root of the tree.

        Returns:
            node [Node]: the newly inserted Node.
        '''
        if self.root is None:
            self.root = Node(data, probability = 1.0)
            return
        if root is None:
            return Node(data, probability = 1.0)
        if root.data != data:
            root.next = self.__ll_insert_node(data, root.next)
        return root

    def __gen_priorities(self):
        '''
        Generates the priorities for the symptoms in the DecisionTree.__causes and initializes
        the Linked List.

        Args:
            None

        Returns:
            None
        '''
        pq = PriorityQueue()
        symptoms = DecisionTree.__frequencies
        pool_size = len(symptoms)
        for symptom in symptoms:
            ratio = symptoms[symptom] / pool_size
            ratio *= -1 # Convert the PQ into a Max PQ
            pq.put((ratio, symptom))
        while not pq.empty():
            ratio, symptom = pq.get()
            # print(f'{(ratio * -100):.2f}% {symptom}')
            self.__ll_insert_node(symptom, self.root)

    def __sort_symptoms(self):
        '''
        Sorts the symptoms in each tuple (rule, symptoms, probability) on the DecisionTree.__causes
        by the priorities contained in DecisionTree.__priorities.

        Args:
            None

        Returns:
            None
        '''
        new_rules = []
        priority = 0
        keys = list(DecisionTree.__frequencies.keys())
        keys.sort(key=lambda a: a, reverse=True)
        keys.sort(key=lambda a: DecisionTree.__frequencies[a])
        for k in keys:
            DecisionTree.__priorities[k] = priority
            priority += 1
        for rule, symptoms, probability in DecisionTree.__causes:
            symptoms = sorted(symptoms, reverse=True, key=lambda a: DecisionTree.__priorities[a])
            new_rules.append((rule, symptoms, probability))
            if rule.startswith('C '):
                DecisionTree.__priorities[rule] = -1
        DecisionTree.__causes = new_rules

    def __build_children_aux(self, root: Node, visited: set = None, path: set = None):
        '''
        Recursively builds all the children for the currrent subtree.

        Args:
            root [Node]: the root for the subtree.
            visited [set]: a set containing the visited nodes of the Linked List.
            path [set]: this argument should not be provided as it's automatically generated.
                It corresponds to the current traversed vertical path.

        Returns:
            None
        '''
        if not root:
            return
        if not visited:
            visited = set()
            visited.add(root.data)
        if not path:
            path = set()
            path.add(root.data)
        for rule, symptoms, probability in DecisionTree.__causes:
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
                    self.__build_children_aux(child, visited, new_path)
                break
        if root.next:
            visited.add(root.next.data)
            self.__build_children_aux(root.next, visited)

    def __build_children(self):
        '''
        Builds the subtree for each node on the Linked List.

        Args:
            None

        Returns:
            None
        '''
        root = self.root
        visited = set()
        while root:
            visited.add(root.data)
            self.__build_children_aux(root, visited)
            root = root.next

    def __get_ll_node_by_symptoms(self, symptoms, root):
        '''
        Gets the first node on the Linked List that corresponds to any of the provided symptoms.

        Args:
            symptoms [array-like]: the array with the symptoms to be corresponded.
            root [Node]: the root for the DecisionTree.

        Returns:
            node [Node]: the first node that corresponds to any of the provided symptoms.
            None: if it does not find a node with the provided symptoms.
        '''
        while root:
            if root.data in symptoms:
                return root
            root = root.next

    def __define_causes(self):
        '''
        Defines the closed-case causes provided by each line on the DecisionTree.__causes.

        Args:
            None

        Returns:
            None
        '''
        for rule, symptoms, probability in DecisionTree.__causes:
            node = self.__get_ll_node_by_symptoms(symptoms, self.root)
            symptoms_tmp = {i for i in symptoms if i != node.data}
            while symptoms_tmp:
                for child in node.children:
                    search = self.__get_ll_node_by_symptoms(symptoms_tmp, child)
                    if not search:
                        continue
                    if len(symptoms_tmp) > 1 and not search.children:
                        continue
                    node = search
                    symptoms_tmp.remove(node.data)
                    break
            node.children.add(Node(rule, probability=probability))

    def __process_probabilities(self):
        '''
        This function will process the rules that start with 'S ...'.
        '''
        pass

    def __compute_probabilities_aux(self, root: Node):
        '''
        Recursively computes the probabilities for all the nodes on the tree.

        Args:
            root [Node]: the root the the current subtree.

        Returns:
            None
        '''
        pool_size = sum([1 if not i.probability else 0 for i in root.children])
        if not pool_size:
            return
        current_probabilities = sum(i.probability if i.probability else 0 for i in root.children)
        random_variables_prob = (1 - current_probabilities) / pool_size
        for child in root.children:
            if not child.probability:
                child.probability = random_variables_prob
            self.__compute_probabilities_aux(child)

    def __compute_probabilities(self):
        '''
        Computes the probabilities for each node on the Linked List.

        Args:
            None

        Returns:
            None
        '''
        root = self.root
        while root:
            self.__compute_probabilities_aux(root)
            root = root.next

    def __build_tree(self):
        self.__compute_frequencies()
        self.__gen_priorities()
        self.__sort_symptoms()
        self.__build_children()
        self.__define_causes()
        # self.__process_probabilities()
        self.__compute_probabilities()

    def search(self, symptoms):
        '''
        Searches for a cause, given ALL symptoms corresponding to it.

        Args:
            symptoms [array-like]: all the symptoms for the cause.

        Returns:
            results [list]: a list containg the possible causes for that array of symptoms.
        '''
        node = self.__get_ll_node_by_symptoms(symptoms, self.root)
        symptoms_tmp = {i for i in symptoms if i != node.data}
        while symptoms_tmp:
            children = list(node.children)
            children.sort(reverse=True, key=lambda a: (DecisionTree.__priorities[a.data], a.data))
            for child in children:
                if child.data in symptoms_tmp:
                    node = child
                    symptoms_tmp.remove(child.data)
                    break
        results = [i.data for i in node.children if i.data.startswith('C ')]
        return results

    def display(self, root, indent=0):
        '''
        Displays the tree strucutre.

        Args:
            root [Node]: the root for the tree.

        Returns:
            None
        '''
        if root:
            print('    ' * indent, end='')
            print(f'{root.data}, {root.probability:.2f}')
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
    ('C Levi Ackerman', {'Olhos azuis', 'Roupa verde', 'Sapato preto'}, 0.2),
    ('C Haachama', {'CHAMACHAMA'}, 1.0),
    ('S Cabelo ruivo', {'Olhos azuis', 'Roupa branca'}, 0.8)
    ('C Levi Ackerman', {'Olhos azuis', 'Sapato preto', 'Roupa verde'}, 0.2),
    ('C Franky', {'Roupa colorida', 'Sapato preto', 'Ser rei'}, 0.12),
    ('C Aurora', {'Olhos azuis', 'Sapato azul'}, 0.92),
]

tree = DecisionTree(rules=rules_expanded)
tree.display(tree.root)


print('\nDecisions with accurate symptoms:')
for rule, symptoms, probability in rules_expanded:
    if not rule.startswith('C '):
        continue
    print('\tSymptoms:', *symptoms)
    print('\t\tExpected:', rule)
    obtained = tree.search(symptoms)
    print('\t\tObtained:', *obtained)
    assert rule == obtained[-1]

print('\nDecisions with innacurate symptoms:')
print('(To-Do)')

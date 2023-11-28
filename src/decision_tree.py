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

    def __hash__(self) -> int:
        return hash(self.data)


class DecisionTree:
    symptoms = dict()
    priorities = dict()
    rules = None

    def __init__(self, rules) -> None:
        self.root = None
        DecisionTree.rules = rules

    def _compute_frequencies(self):
        '''
        Builds a dict counting the frequencies of the symptoms on the DecisionTree.rules.

        Args:
            None

        Returns:
            None
        '''
        frequencies = dict()
        for rule, symptoms, _ in DecisionTree.rules:
            for symptom in symptoms:
                if not rule.startswith('C '):
                    continue
                if symptom not in frequencies:
                    frequencies[symptom] = 0
                frequencies[symptom] += 1
        DecisionTree.symptoms = frequencies

    def _ll_insert_node(self, data, root):
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
            root.next = self._ll_insert_node(data, root.next)
        return root

    def _gen_priorities(self):
        '''
        Generate the priorities for the Decision Tree's symptoms.

        Args:
            None

        Returns:
            None
        '''
        pq = PriorityQueue()
        symptoms = DecisionTree.symptoms
        pool_size = len(symptoms)
        for symptom in symptoms:
            ratio = symptoms[symptom] / pool_size
            ratio *= -1 # Convert the PQ into a Max PQ
            pq.put((ratio, symptom))
        while not pq.empty():
            ratio, symptom = pq.get()
            # print(f'{(ratio * -100):.2f}% {symptom}')
            self._ll_insert_node(symptom, self.root)

    def _get_ll_node_by_symptoms(self, symptoms, root):
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

    def _sort_symptoms(self):
        '''
        Sorts the symptoms of the DecisionTree by the priorities contained in DecisionTree.priorities.

        Args:
            None

        Returns:
            None
        '''
        new_rules = []
        priority = 0
        keys = list(DecisionTree.symptoms.keys())
        keys.sort(key=lambda a: a, reverse=True)
        keys.sort(key=lambda a: DecisionTree.symptoms[a])
        for k in keys:
            DecisionTree.priorities[k] = priority
            priority += 1
        for rule, symptoms, probability in DecisionTree.rules:
            symptoms = sorted(symptoms, reverse=True, key=lambda a: DecisionTree.priorities[a])
            new_rules.append((rule, symptoms, probability))
            if rule.startswith('C '):
                DecisionTree.priorities[rule] = -1
        DecisionTree.rules = new_rules

    def __build_children(self, root: Node, visited: set = None, path: set = None):
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
                    self.__build_children(child, visited, new_path)
                break
        if root.next:
            visited.add(root.next.data)
            self.__build_children(root.next, visited)

    def _build_children(self):
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
            self.__build_children(root, visited)
            root = root.next

    def _define_causes(self):
        '''
        Defines the closed-case causes provided by each line on the DecisionTree.rules.

        Args:
            None

        Returns:
            None
        '''
        for rule, symptoms, probability in DecisionTree.rules:
            node = self._get_ll_node_by_symptoms(symptoms, self.root)
            symptoms_tmp = {i for i in symptoms if i != node.data}
            while symptoms_tmp:
                for child in node.children:
                    search = self._get_ll_node_by_symptoms(symptoms_tmp, child)
                    if not search:
                        continue
                    if len(symptoms_tmp) > 1 and not search.children:
                        continue
                    node = search
                    symptoms_tmp.remove(node.data)
                    break
            node.children.add(Node(rule, probability=probability))

    def process_probabilities(self):
        '''
        This function will process the rules that start with 'S ...'.
        '''
        pass

    def __compute_probabilities(self, root: Node):
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
            self.__compute_probabilities(child)

    def _compute_probabilities(self):
        '''
        Computes the probabilities for each node on the Linked List.

        Args:
            None

        Returns:
            None
        '''
        root = self.root
        while root:
            self.__compute_probabilities(root)
            root = root.next

    def _search(self, symptoms):
        '''
        Searches for a cause, given all symptoms corresponding to it.

        Args:
            symptoms [array-like]: all the symptoms for the cause.

        Returns:
            results [list]: a list containg the possible causes for that array of symptoms.
        '''
        node = self._get_ll_node_by_symptoms(symptoms, self.root)
        symptoms_tmp = {i for i in symptoms if i != node.data}
        while symptoms_tmp:
            children = list(node.children)
            children.sort(reverse=True, key=lambda a: (DecisionTree.priorities[a.data], a.data))
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
            print(f'{root.data}, {root.probability:.1f}')
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
tree._compute_frequencies()
tree._gen_priorities()
tree._sort_symptoms()
tree._build_children()
tree._define_causes()
tree._compute_probabilities()
tree.display(tree.root)

print('\nDecisions with accurate symptoms:')
for rule, symptoms, probability in rules_expanded:
    print(*symptoms)
    print('Expected:', rule, probability)
    obtained = tree._search(symptoms)
    print('Obtained:', *obtained, probability)
    assert rule == obtained[-1]

print('\nDecisions with innacurate symptoms:')
print('(To-Do)')
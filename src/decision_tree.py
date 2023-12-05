import numpy as np
from queue import PriorityQueue
from sklearn import preprocessing


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
        self.__selected_node = None

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

    def __gen_priorities(self):
        '''
        Generates the priorities for the symptoms in the DecisionTree.__causes and initializes
        the Linked List.

        Args:
            None

        Returns:
            None
        '''
        priority = 0
        keys = list(DecisionTree.__frequencies.keys())
        keys.sort(key=lambda a: a, reverse=True)
        keys.sort(key=lambda a: DecisionTree.__frequencies[a])
        for k in keys:
            DecisionTree.__priorities[k] = priority
            priority += 1

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
            node = Node(data, probability = 1.0)
            self.root = node
            return node
        if root is None:
            return Node(data, probability = 1.0)
        if root.data != data:
            root.next = self.__ll_insert_node(data, root.next)
        return root

    def __ll_initialize(self):
        '''
        Initializes the Linked List with the priorities contained in DecisionTree.__priorities.

        Args:
            None

        Returns:
            None
        '''

        pq = PriorityQueue()
        for symptom in DecisionTree.__priorities:
            pq.put((-1 * DecisionTree.__priorities[symptom], symptom))
        while not pq.empty():
            _, symptom = pq.get()
            self.__ll_insert_node(symptom, self.root)

    def __causes_priorities(self):
        '''
        Sorts the symptoms in each tuple (rule, symptoms, probability) on the DecisionTree.__causes
        by the priorities contained in DecisionTree.__priorities.

        Args:
            None

        Returns:
            None
        '''
        new_rules = []
        for rule, symptoms, probability in DecisionTree.__causes:
            symptoms = sorted(symptoms, reverse=True, key=lambda a: DecisionTree.__priorities[a])
            new_rules.append((rule, symptoms, probability))
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

    def __define_inconsistent_causes_aux(self, root: Node, path: set = None):
        '''
        Recursively distributes the causes throughout the subtree, already defining their
        fractional probabilities.

        Args:
            root [Node]: the root to the subtree.
            path [set]: this argument should not be provided as it's automatically generated.
                It corresponds to the current traversed vertical path.

        Returns:
            None
        '''
        if not path:
            path = set()
        path.add(root.data)
        for cause, symptoms, probability in DecisionTree.__causes:
            if len(path.intersection(symptoms)) != len(path):
                continue
            if root.data in symptoms:
                pool_size = len(symptoms)
                probability_fraction = len(path)
                probability_fraction = probability_fraction / pool_size
                new_probability = probability_fraction * probability
                root.children.add(Node(cause, probability=new_probability))
            for child in root.children:
                path_copy = {i for i in path}
                self.__define_inconsistent_causes_aux(child, path_copy)

    def __define_inconsistent_causes(self):
        '''
        Defines the causes when the symptoms are inconsistent, i.e. when not
        all symptoms were provided for a cause.

        Args:
            None

        Returns:
            None
        '''
        root = self.root
        while root:
            self.__define_inconsistent_causes_aux(root)
            root = root.next

    def __process_probabilities_aux(self, root: Node, stack: list, probability):
        '''
        Recursively searches a given subtree for a node with all the elements
        present in stack and define its probability.

        Args:
            root [Node]: the root for the subtree.
            stack [list]: a stack, where its first element is the node whose probability
            will be defined.
            probability [float]: the probability.

        Returns:
            None
        '''
        if not root:
            return
        if not stack:
            return
        if len(stack) == 1 and root.data == stack[-1]:
            root.probability = probability
            return
        for child in root.children:
            if child.data == stack[-1] and len(stack) > 1:
                self.__process_probabilities_aux(child, stack[:-1], probability)
            else:
                self.__process_probabilities_aux(child, stack[:], probability)

    def __process_probabilities(self):
        '''
        This function will process the rules that start with 'S ' and define the probability for
        each rule in DecisionTree.__symptoms.

        Args:
            None

        Returns:
            None
        '''
        root = self.root
        while root:
            for rule, symptoms, probability in DecisionTree.__symptoms:
                stack = [rule[2:]]
                sorted_stack = [i for i in symptoms if i in DecisionTree.__priorities]
                sorted_stack.sort(key=lambda a: a, reverse=True)
                sorted_stack.sort(key=lambda a: DecisionTree.__priorities[a])
                stack.extend(sorted_stack)
                if root.data == stack[-1]:
                    stack.pop()
                self.__process_probabilities_aux(root, stack, probability)
            root = root.next

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

    def __normalize_probabilities_aux(self, root: Node):
        '''
        Given a node, normalize all the probabilities from its children so they sum up to 1.
        This function also sorts the children by their probabilities.

        Args:
            root [Node]: the node whose children's probabilities will be normalized.

        Returns:
            None
        '''
        nodes = [i for i in root.children]
        if not nodes:
            return
        if len(nodes) == 1:
            return
        probabilities = [i.probability for i in nodes]
        probabilities = np.array(probabilities)
        min_range = min(abs(i) for i in probabilities)
        min_range = min(min_range, 1.0)
        max_range = max(abs(i) for i in probabilities)
        max_range = min(max_range, 1.0)
        probabilities = probabilities.reshape(-1, 1)
        probabilities_scaled = preprocessing.minmax_scale(probabilities, feature_range=(min_range, max_range))
        probabilities_scaled = probabilities_scaled.flatten()
        total_sum = probabilities_scaled.sum()
        for i in range(len(nodes)):
            node = nodes[i]
            node.probability = probabilities_scaled[i] / total_sum
        root.children = sorted(root.children, key=lambda a: (a.data))
        root.children = sorted(root.children, key=lambda a: (a.probability), reverse=True)
        root.children = sorted(root.children, key=lambda a: 1 if a.data.startswith('C ') else 0)
        for child in root.children:
            self.__normalize_probabilities_aux(child)

    def __normalize_probabilities(self):
        '''
        Normalizes the probabilities on all subtree levels so they add up to 1.0.

        Args:
            None

        Returns:
            None
        '''
        root = self.root
        while root:
            self.__normalize_probabilities_aux(root)
            root = root.next

    def __build_tree(self):
        '''
        Builds the whole tree structure, calling every
        function following the correct order.
        This method should be only called by the
        tree's constructor.

        Args:
            None

        Returns:
            None
        '''
        self.__compute_frequencies()
        self.__gen_priorities()
        self.__ll_initialize()
        self.__causes_priorities()
        self.__build_children()
        self.__define_causes()
        self.__define_inconsistent_causes()
        self.__process_probabilities()
        self.__compute_probabilities()
        self.__normalize_probabilities()

    def __to_dict_aux(self, root: Node, tree_dict: dict = None):
        '''
        Recursively traverses a subtree, storing its children and probabilities in dictionaries.

        Args:
            root [Node]: the root for the subtree.
            tree_dict [dict]: the dictionary to-be update with the tree structure.

        Returns:
            None
        '''
        if not root:
            return
        root_node = (root.data, root.probability)
        if root_node not in tree_dict:
            tree_dict[root_node] = []
        for child in root.children:
            new_dict = dict()
            new_node = (child.data, child.probability)
            new_dict[new_node] = []
            tree_dict[root_node].append(new_dict)
            self.__to_dict_aux(child, new_dict)

    def to_dict(self):
        '''
        Gets the tree structure as a Python dictionary.

        Args:
            None

        Returns:
            tree_dict [dict]: a dictionary containing the entire tree structure, following the pattern:
                (symptom/cause, probability): [children]
        '''
        tree_dict = dict()
        root = self.root
        while root:
            self.__to_dict_aux(root, tree_dict)
            root = root.next
        return tree_dict

    def decide(self, decision: str = None):
        '''
        Traverses the tree based on questions and answers.

        Args:
            decision [str | None]: the symptom selected by the user.
                If decision is None, then this function will assume that
                the search is at its beginning.

        Returns:
            options [tuple]: the options for the user to chose. Once the
                user has selected "YES" for any of these options, then this
                option becomes the next decision.
                The options tuple is ordered by the priority of the symptoms,
                then by the priority of the causes. Symptoms have priority over causes.
                Each element of the tuple consists of (str, float), which is the
                symptom and its probability.
        '''
        options = []
        if not decision:
            self.__selected_node = None
            root = self.root
            while root:
                options.append((root.data, root.probability))
                root = root.next
        elif decision.startswith('C '):
            return
        elif not self.__selected_node:
            root = self.root
            while root and root.data != decision:
                root = root.next
            options = [(i.data, i.probability) for i in root.children]
            self.__selected_node = root
        else:
            for child in self.__selected_node.children:
                if child.data == decision:
                    self.__selected_node = child
            options = [
                (i.data, i.probability) for i in self.__selected_node.children]
        return tuple(options)

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


def main():
    rules_expanded = [
        ('C Naruto Uzumaki', {'Olhos azuis', 'Roupa laranja', 'Sapato azul', 'NOT Dor'}, 0.5),
        ('C Hinata Shouyou', {'Roupa laranja', 'Sapato branco', 'NOT Olhos azuis'}, 0.6),
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
        ('C Haachama', {'CHAMACHAMA'}, 1.0),
        ('S Sapato marrom', {'Olhos azuis', 'Roupa branca'}, 0.8),
        ('S Cabelo ruivo', {'Roupa branca'}, 0.91),
        ('S Armadura azul', {'Cabelo preto'}, 0.67),
        ('S Botas brancas', {'Cabelo preto'}, 0.84)
    ]

    tree = DecisionTree(rules=rules_expanded)

    print('*************************')
    print('* Estrutura da árvore:  *')
    print('*************************\n')
    tree.display(tree.root)

    '''
    O exemplo abaixo explica a lógica para decisão e travessia pela árvore.

    Os outros exemplos não estão explicados, mas seguem a mesma lógica.
    '''
    print('\n')
    print('*************************')
    print('* Exemplo de decisão 1: *')
    print('*************************\n')
    print('Sintomas a partir da raiz:')
    from_root = tree.decide() # Chamar a função sem argumentos para receber as opções inciais
    for c, _ in from_root:
        print(c)
    print('Esses são os sintomas que devemos começar perguntando, nessa ordem, ao usuário.')
    print('')
    symptom = 'Roupa laranja'
    options = tree.decide(symptom) # Chamar a função com o sintoma selecionado, para efetuar a travessia
    print(f'Caso personagem tenha apenas o sintoma *{symptom}*, as opções serão:')
    for c, p in options:
        print(f'Regra: {c:<30}', f'Probabilidade: {(p*100):.2f}%')
    print('')
    max_probability = max(i[1] for i in options if i[0].startswith('C '))
    decision = [i for i in options if i[0].startswith('C ') and i[1] == max_probability]
    cause = decision[0][0]
    cause = cause[2:]
    probability = (decision[0][1]*100)
    print(f'E a decisão será a *causa* com maior probabilidade, ou seja:', cause)
    print(f'com a confiança de {probability:.2f}%.')

    '''
    Esses exemplos mostram como funciona a função de decisão, etapa por etapa.

    Caso o usuário responda com "Não sei", basta selecionar a causa com maior probabilidade,
    que foi a lógica usada no exemplo anterior.
    '''
    print('\n')
    print('*************************')
    print('* Exemplo de decisão 2: *')
    print('*************************\n')
    print(*tree.decide(), '\n')
    print(*tree.decide('Olhos azuis'), '\n')
    print(*tree.decide('Roupa branca'), '\n')
    print(*tree.decide('Sapato marrom'), '\n')
    print(*tree.decide('Cabelo ruivo'))
    print('\n')
    print('*************************')
    print('* Exemplo de decisão 3: *')
    print('*************************\n')
    print(*tree.decide(), '\n')
    print(*tree.decide('Cabelo preto'), '\n')
    print(*tree.decide('Armadura azul'), '\n')
    print(*tree.decide('Botas brancas'))


if __name__ == '__main__':
    main()

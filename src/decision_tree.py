import numpy as np
from queue import PriorityQueue
from sklearn import preprocessing
from concurrent.futures import ThreadPoolExecutor, wait


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
        self.__decision_queue = []
        self.__decision = None

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
                new_path = path.copy()
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
        with ThreadPoolExecutor() as executor:
            root = self.root
            visited = set()
            futures = []
            while root:
                visited.add(root.data)
                future = executor.submit(self.__build_children_aux, root, visited.copy())
                futures.append(future)
                root = root.next
            wait(futures)

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
            symptoms_sorted = sorted(symptoms, key=lambda a: (self.__priorities[a], a), reverse=True)
            subtree = self.__get_ll_node_by_symptoms(symptoms_sorted[0], self.root)
            symptoms_sorted = symptoms_sorted[1:]
            for symptom in symptoms_sorted:
                for child in subtree.children:
                    if child.data == symptom:
                        subtree = child
                        break
            subtree.children.add(Node(rule, probability=probability))

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
                path_copy = path.copy()
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
        subtrees = []
        while root:
            subtrees.append(root)
            root = root.next
        with ThreadPoolExecutor() as executor:
            executor.map(self.__define_inconsistent_causes_aux, subtrees)

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
        subtrees = []
        while root:
            subtrees.append(root)
            root = root.next
        with ThreadPoolExecutor() as executor:
            executor.map(self.__compute_probabilities_aux, subtrees)

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
        if min_range == max_range:
            min_range -= 0.1
            max_range += 0.1
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
        subtrees = []
        while root:
            subtrees.append(root)
            root = root.next
        with ThreadPoolExecutor() as executor:
            executor.map(self.__normalize_probabilities_aux, subtrees)

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
        print('Initializing Linked List')
        self.__compute_frequencies()
        self.__gen_priorities()
        self.__ll_initialize()
        self.__causes_priorities()
        print('Building children')
        self.__build_children()
        print('Defining causes')
        self.__define_causes()
        print('Defining causes with partial symptoms')
        self.__define_inconsistent_causes()
        print('Processing probabilities')
        self.__process_probabilities()
        self.__compute_probabilities()
        self.__normalize_probabilities()
        print('DecisionTree successfully loaded!')

    def __to_dict_aux(self, root: Node, tree_dict: dict = None, i = 0):
        '''
        Recursively traverses a subtree, storing its children and probabilities in dictionaries.

        Args:
            root [Node]: the root for the subtree.
            tree_dict [dict]: the dictionary to-be updated with the tree structure.
            i [int]: the priority for the current node.

        Returns:
            None
        '''
        if not root:
            return
        root_node = f'{i:06}, {root.data}, {(root.probability*100):.8f}%'
        if root_node not in tree_dict:
            tree_dict[root_node] = dict()
        for child in root.children:
            i+=1
            new_dict = dict()
            new_node = f'{i:06}, {child.data}, {(child.probability*100):.8f}%'
            tree_dict[root_node][new_node] = new_dict
            self.__to_dict_aux(child, tree_dict[root_node], i)

    def to_dict(self):
        '''
        Gets the tree structure as a Python dictionary.

        Args:
            None

        Returns:
            tree_dict [dict]: a dictionary containing the entire tree structure, following the pattern:
                {"Number, Data, Probability%": children[dict]}

                The "Number" in each node is useful for sorting reasons, since the priority is
                fundamental for displaying the tree. This function supports trees with up to
                10e6 nodes.
        '''
        tree_dict = dict()
        root = self.root
        i = 0
        while root:
            self.__to_dict_aux(root, tree_dict, i)
            i+=1
            root = root.next
        return tree_dict

    def __decide_aux(self, decision: str = None):
        '''
        Traverses the tree based on questions and answers.

        Args:
            decision [str | None]: the symptom selected by the user.
                If decision is None, then this function will assume that
                the search is at its beginning.

        Returns:
            options [list]: the options for the user to chose. Once the
                user has selected "YES" for any of these options, then this
                option becomes the next decision.
                The options tuple is ordered by the priority of the symptoms (ascending order),
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
        return options[::-1]

    def decide(self, answer: str = None):
        '''
        Decide function for the DecisionTree.

        Args:
            answer [str]: can be None, 'yes', 'no', or 'doubt'.
            None: setup the tree for decision. Should be called only before
                the decision process;
            'yes': the answer is "yes" for the
                DecisionTree.decision;
            'no': the answer is "no" for the
                DecisionTree.decision;
            'doubt': the answer is "doubt" for the
                DecisionTree.decision.

        Returns:
            None
        '''
        if answer is None:
            self.__decision_queue = self.__decide_aux()
        if answer not in ['yes', 'no', 'doubt', None]:
            raise Exception('Answer needs to be None, "yes", "no" or "doubt"!')
        elif answer == 'yes':
            self.__decision_queue = self.__decide_aux(self.__decision_queue[-1][0])
        elif answer == 'no':
            self.__decision_queue.pop()
        elif answer == 'doubt':
            self.__decision_queue.pop() # Make the "doubt" work the same as the "no" option.
            # while self.__decision_queue and not self.__decision_queue[-1][0].startswith('C '):
            #     self.__decision_queue.pop()
        if self.__decision_queue:
            self.__decision = self.__decision_queue[-1]
        else:
            self.__decision = None

    @property
    def decision(self):
        return self.__decision

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

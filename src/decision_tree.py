
"""
Sintoma-Causa Decision Tree:
    This decision tree has 4 branches for each decision node.

    Branch name     :       Meaning
    ------------------------------------------------------------------------------------------------
    yes             :       path contains sintoma n
    no              :       path does not contain sintoma n (represented by !n)
    unknown         :       path does not contain information about the current symptom evaluated by
    results         :       leaves with the possible causes for symptons path
    ------------------------------------------------------------------------------------------------

    The leaves represent the outcome of the "sintomas"
    Each path represents a relationship "sintoma a, NOT sintoma b, ... , sintoma c :  causa n"

"""
#####  funcoes que precisam ser feitas : search result (achar a probabilidade de uma causa acontecer dado sintoma 2, 3 !4)

#####  funcoes que nao sei como fazer  : implementar sintoma com grau de certeza(n sei como fazer isso, aqui ta como valores discretos, 0, 1 ou s/ info)   
#####                                  : implementar sintoma como resultado ? 
class Node:
    
    # atributos necessarios para avaliar a o caminho a ser realizado

    def __init__(self, probability, name, is_leaf=False, ):
        self.yes = None
        self.no = None
        self.unknown = None
        self.results = []

        self.probability = probability
        self.name = name
        self.is_leaf = is_leaf
      
    def printNode(self):
        print(self.name, self.probability)

    def addResult(self, result_name, result_probability):
        self.results.append(Node(name=result_name, probability= result_probability, is_leaf=True))

    def insertNode(self, path_list, probability, depth=0):
        next_step = path_list[0]

    # primeiro if: avalia se o caminho chegou ao fim e adiciona resultado

        if len(path_list) == 1:
            self.addResult(result_name=f"causa {next_step}", result_probability=probability)
    
        else:

    # segundo if: verifica se o caminho possui diretivas de NOT, e adciona node ao ponteiro self.no caso sim
            if next_step[0] == "!":

                if int(next_step[1]) != depth:
                    self.unknown = Node(probability=probability, is_leaf=False, name=f"no do resultado de decisao sintoma {depth}")
                    self.unknown.insertNode(path_list=path_list, probability=probability, depth=depth+1)

    # elif do nao : se ja existir um caminho nao, nao muda nada nesse caminho e apenas altera o final do caminho MUDAR!!!
                elif self.no:
                    self.no.insertNode(path_list=path_list[1:], probability=probability, depth=depth+1)

    # else do nao : nesse caso nao existe uma decisao do tipo NAO conectada ao noda, cria-se esse node e continua-se o caminho 
                else:
                    self.no = Node(probability=probability, is_leaf=False, name=f"no de do resultado decisao sintoma {depth}")
                    self.no.insertNode(path_list=path_list[1:], probability=probability, depth=depth+1)

            else:

    # if, elif e else do caminho sim sao analogos ao caminho nao

                if int (next_step[0]) != depth:
                    self.unknown = Node(probability=probability, is_leaf=False, name=f"no do resultado de decisao sintoma {depth}")
                    self.unknown.insertNode(path_list=path_list, probability=probability, depth=depth+1)
                
                elif self.yes:
                    self.yes.insertNode(path_list[1:], probability, depth=depth+1)

                else:
                    self.yes = Node(probability=probability, is_leaf=False, name=f"no de do resultado decisao sintoma {depth}")
                    self.yes.insertNode(path_list=path_list[1:], probability=probability, depth=depth+1)





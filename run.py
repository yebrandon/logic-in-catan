from nnf import Var
from lib204 import Encoding
from tree import buildTree, findLeaves, findAllParents

givenBoardCondition = ["Wo_11 >> (Wh_21 || Sh_22)", "Wh_21 >> Br_31", "Wh_21 >> Wo_32", "Sh_22 >> Wo_31"]
S = ["Wh", "Wo", "Br"] #set of nodes required for a winning branch
k = 3 #maximum amount of steps required to find a winning branch


'''
This function creates variables of Var type and stores them in a variable dictionary from an input board condition. 
Parameters: takes in a list of strings representing givenBoardCondition of n nodes organized by implications and or logical operators. And k, an integer variable representing the amount of steps allowed for a path to be found in. 
Returns: a dictionary of resource variables of Var type that does not contain any variables after the kth row. 
'''
def createVariables(givenBoardCondition,k):
    #creating dictionaries for each resource to hold their resources
    whVariables = {}
    brVariables = {}
    woVariables = {}
    shVariables = {}
    variableDictionary = {}

    #Running through each list value in the given board condition and splitting them based on the operators to just leave variable names ie. W_31
    #Then creating a dictionary key value pair where the key is the variable name and the value is a Var with the variable name used as the 
    # constructor value
    for node in givenBoardCondition:
        parts=node.replace(">>"," ").replace("&"," ").replace("|"," ").replace("("," ").replace(")"," ").split()
        for variable in parts:
            variable.strip()
            #if variables are greater than k, they are not included in the final dictionary
            if(int(variable[3]) <= k+1):
              if "wh" in variable.lower():
                  whVariables[variable] = Var(variable) 
              if "wo" in variable.lower():
                  woVariables[variable] = Var(variable)
              if "br" in variable.lower():
                  brVariables[variable] = Var(variable)
              if "sh" in variable.lower():
                  shVariables[variable] = Var(variable)
    
    #Merging variable dictionaries into 1 master dictionary containing all variables 
    variableDictionary = mergeDictionaries(variableDictionary,whVariables,woVariables,shVariables,brVariables)
    return variableDictionary

'''
Helper method to merge two dictionaries together, as long as both dictionaries are not null.
Parameters: overall variable dictionary to be merged with the dictionary containing the wheat, brick, wood and sheep values of the tree. 
Returns: merged dictionary of all variables
'''   
def mergeDictionaries(variableDictionary,whVariables,woVariables,shVariables,brVariables):
    #checks to see if the variables dictionary is null, if so copies the contents of resource dictionary to prevent null type error from occuring with update. If not merges the two dictionaries. 
    if not variableDictionary and whVariables:
      variableDictionary = whVariables.copy()
    if not variableDictionary and woVariables:
      variableDictionary = woVariables.copy()
    elif variableDictionary and woVariables:
      variableDictionary.update(woVariables)
    if not variableDictionary and brVariables:
      variableDictionary = brVariables.copy()
    elif variableDictionary and brVariables:
      variableDictionary.update(brVariables)
    if not variableDictionary and shVariables:
      variableDictionary = shVariables.copy()
    elif variableDictionary and shVariables:
      variableDictionary.update(shVariables)
      
    return variableDictionary
    
    
def createBoardConstraints(givenBoardCondition, variables, E, k):
  """Adds implication constraints to the logical encoding
  Args:
    givenBoardCondition: a list of strings representing the game board configuration
    variables: a dictionary of Var type variables, where the key is a string of the variable name and the value is the matching variable
    E: the logical encoding
    k: an integer representing the maximum number of steps a solution may have
  Returns:
    E: the logical encoding with the implication constraints added
  """
  for node in givenBoardCondition:
      parts=node.replace(">>"," ").replace("&"," ").replace("|"," ").replace("("," ").replace(")"," ").split()
      top = variables[parts[0]]
      connectedNodes = []
      for part in parts:
          if part != parts[0]:
              if int(part[3]) <= k+1:
                  connectedNodes.append(variables[part])
      for node in connectedNodes:
          E.add_constraint(node.negate() | top)
  return E


def createImplicationList(givenBoardCondition,k):
  """Returns all implications in the logical model
  Args:
    givenBoardCondition: a list of strings representing the game board configuration
    k: an integer representing the maximum number of steps a solution may have
  Returns:
    groups: a list of lists of dictionaries, each representing a node in the tree, with the node in the first index of a list being implied by the node in the second index of the list, i.e the node at the first index is "below" and "connected to" the node at the second index.
  """
  
  groups = []
  for node in givenBoardCondition:
    parts = []
    parts=node.replace(">>"," ").replace("&"," ").replace("|"," ").replace("("," ").replace(")"," ").split()
    top = parts[0]
    connectedNodes = []

    for part in parts:
        if part != parts[0]:
            if int(part[3]) <= k+1:
                connectedNodes.append(part)
                
    for node in connectedNodes:
        nodeData = {"res": node[0:2], "row": int(node[3]), "col": int(node[4])}
        topData = {"res": top[0:2], "row": int(top[3]), "col": int(top[4])}
        groups.append([nodeData,topData])
        
  return groups

#creates lists containing each of the common variables, based on node type, in the dictionary 
def createVariableLists(variables):
  """Returns lists containing each of the common variables based on node type
  Args:
    variables: a dictionary of Var type variables
  Returns:
    wood, wheat, sheep, brick: lists of strings each representing nodes that are of the list's node type
  """
  wood, wheat, brick, sheep = [], [], [], []
  for key in variables:
    if "Wh" in key:
      wheat.append(key)
    elif "Wo" in key:
      wood.append(key)
    elif "Br" in key:
      brick.append(key)
    elif "Sh" in key:
      sheep.append(key)
  return wood, wheat, sheep, brick

'''
The following three functions take each of the leaves and creates a constraint based on the idea that if one leaf is chosen that leaf implies its parent node, which in turn implies its parent node all the way to the root (ie, for every leaf there is one path in the tree). However, only one of these paths can be true at one time. The function creates n contstraints where n is the length of leaf-list, in the form of leaf1 >> !leaf2 and !leaf3 ... !leafn, leaf2 >> !leaf1 ... ect.  
Parameters: list of leaf dictionaries, the encoding E, and the variables dictionary. 
Returns: Encoding E with added constraints
'''
def leaf_constraints(leaf_list,E,variables):
    for leaf in leaf_list:
        other_leaves = [] #array to contain the leaves that are not the current leaf
        for next_leaf in leaf_list:
            if next_leaf != leaf:
                other_leaves.append(next_leaf)
        #adding constraint to course library E for the current leaf
        
        E.add_constraint(dict_to_var(leaf, variables).negate() |( set_leaf_constraint(other_leaves,variables)))
    return E
 
'''
Helper method that returns a new constraint based on the leaf array, in the the form of leaf >> !leaf2 and !leaf3 ...
Parameters: other_leaves as list of leaf dictionaries minus the current leaf, and the variables dictionary
Returns: a new constraint to be added to E
'''
def set_leaf_constraint(other_leaves,variables):
    for other in other_leaves:
        var = dict_to_var(other,variables)
        #if not at the last node add the current leaf Var negated to the constraint with &. Otherwise, add the leaf constraint normally to the current constraint. 
        if other == other_leaves[0]:
          new_constraint = var.negate()
        else:
          new_constraint &= var.negate()
            #new_constraivar.negate() & new_constraint  new_constraint + "!" + str + "&"
    return new_constraint

'''
Helper method that converts String dictionary to Var value so it can be added to a constraint. 
Parameters: some leaf dictionary and the variables dictionary
Returns: Associated Var Node that matches the leaf
'''
def dict_to_var(leaf,variables):
    var = ""
    var = leaf["res"] + "_" + str(leaf["row"]) + str(leaf["col"])
    return variables[var]

'''
A function that creates the required constraints for overall variables Wh, Sh, Br, Wo. Each node of a certain type implies the corresponding overall type and if all nodes of a type are false, the overall variable is false.
Parameters: All 4 overall variables, variable dictionary, variable node type lists, E
Returns: E after constraints have been added 
'''
def setOverallVariablesTrueOrFalse(Wh, Wo, Br, Sh, variables, wood, wheat, sheep, brick,E, S):  
    if "Wo" in S:
      new_constraint = False
      for node in wood:
        E.add_constraint(variables[node].negate() | Wo)
        if (node == wood[0]):
          new_constraint = variables[node].negate()
        else:
          new_constraint &= variables[node].negate()
      E.add_constraint(new_constraint.negate() | Wo.negate())
      
    if "Wh" in S:
      new_constraint = False
      for node in wheat:
        E.add_constraint(variables[node].negate() | Wh)
        if (node == wheat[0]):
          new_constraint = variables[node].negate()
        else:
          new_constraint &= variables[node].negate()
      E.add_constraint(new_constraint.negate() | Wh.negate())

    if "Sh" in S:
      new_constraint = False
      for node in sheep:
        E.add_constraint(variables[node].negate() | Sh)
        if (node == sheep[0]):
          new_constraint = variables[node].negate()
        else:
          new_constraint &= variables[node].negate()
      E.add_constraint(new_constraint.negate() | Sh.negate())
      
    if "Br" in S:
      new_constraint = False
      for node in brick:
        E.add_constraint(variables[node].negate() | Br)
        if (node == brick[0]):
          new_constraint = variables[node].negate()
        else:
          new_constraint &= variables[node].negate()
      E.add_constraint(new_constraint.negate() | Br.negate())
    return E

'''
Checks required nodes and provided we don't need to hit a node, 
Parameters: the required nodes, E, overall variables 
Returns: E 
'''
def implementRequiredNodes(S,E,Wo,Wh,Sh,Br):
  if "Wo" not in S:
    E.add_constraint(Wo)
  if "Wh" not in S:
    E.add_constraint(Wh)
  if "Sh" not in S:
    E.add_constraint(Sh)
  if "Br" not in S:
    E.add_constraint(Br)
  return E

"""
Takes in all the variables and returns a 2D list of variables in the same row
Variables in Row 1 goes in the first nested list, Row 2 goes in the second nested list, etc. 
"""
def variablesToRows(variables):
  counter = 0
  for key in variables:
    if int(key[3]) > counter:
      counter = int(key[3]) 
  rowVariables = []
  for x in range(counter+1):
    rowVariables.append([])
  for key in variables:
    row = int(key[3])
    rowVariables[row-1].append(variables[key])
  print(rowVariables)
  return rowVariables

""" Takes in the rowVariables and E and creates constraints so that only node 
from each row can be chosen. Returns E after the constraints have been added"""
def rowVariablesToConstraints(rowVariables,E):
  for row in rowVariables:
    for variable in row:
      for other in row:
        if variable != other:
          E.add_constraint(variable.negate() | other.negate())
  return E

#
# Build an example full theory for your setting and return it.
#
#  There should be at least 10 variables, and a sufficiently large formula to describe it (>50 operators).
#  This restriction is fairly minimal, and if there is any concern, reach out to the teaching staff to clarify
#  what the expectations are.
def example_theory():
  variables=createVariables(givenBoardCondition,k)

  #overall variables for overall node types and winning condition
  Wh = Var("Wh")
  Wo = Var("Wo")
  Sh = Var("Sh")
  Br = Var("Br")
  W = Var("W")

  #create variable arrays
  wood, wheat, sheep, brick = createVariableLists(variables)
  tree = buildTree(variables, createImplicationList(givenBoardCondition,k))
  rowVariables = variablesToRows(variables)

  E = Encoding()
  #Making Constraints based on board condition
  E = createBoardConstraints(givenBoardCondition,variables,E,k)
  #Adding constraint for winning condition
  E.add_constraint(W.
  
negate() | (Wh & Wo & Sh & Br))
  #Setting W to always true so that the solver tries to find a winning model
  E.add_constraint(W)

  E = setOverallVariablesTrueOrFalse(Wh, Wo, Br, Sh, variables, wood, wheat, sheep, brick,E,S)
  E = leaf_constraints(findLeaves(tree,findAllParents(tree,createImplicationList(givenBoardCondition,k))), E, variables)
  E = implementRequiredNodes(S,E,Wo,Wh,Sh,Br)
  E = rowVariablesToConstraints(rowVariables,E)
  #print(findLeaves(tree,findAllParents(tree,createImplicationList(givenBoardCondition,k))))
  print(E.constraints)
  return E


if __name__ == "__main__":
  T = example_theory()

  print("\nSatisfiable: %s" % T.is_satisfiable())
  print("# Solutions: %d" % T.count_solutions())
  print("   Solution: %s" % T.solve())

'''
  print("\nVariable likelihoods:")
  for v,vn in zip([a,b,c,x,y,z], 'abcxyz'):
    print(" %s: %.2f" % (vn, T.likelihood(v)))
  print()
'''
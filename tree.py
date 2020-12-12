# This module contains functions related to creating the game board in a tree structure and accessing the nodes

def removeKey(d, key):
  """Returns a dictionary with a key removed

  Args:
      d: a dictionary
      key: the key to be removed

  Returns:
      copy: a copy of the dictionary d with the key removed

  """
  copy = dict(d)
  del copy[key]
  return copy


def buildTree(varDict, implications):
  """Returns tree of nodes to represent the logical model

  Args:
      varDict: a dictionary of strings representing all variables from the logical model
      implications: a list of string representing all implications from the logical model

  Returns:
      tree: a list of dictionaries each representing a node in the tree

  """
  tree = []
  for key in varDict:
    tree.append({"res":key[0:2], "row":int(key[3]), "col":int(key[4])})
  tree = sorted(tree, key=lambda i: i['row'])
  
  for node in tree:
    parents = []
    for implication in implications:
      if node == implication[0]:
        parents.append(implication[1])
    node["parents"] = parents
  return(tree)


def findAllParents(tree, implications):
  """Returns all nodes that are parents, i.e have at least one child

  Args:
      tree: a list of dictionaries each representing a node in the tree

  Returns:
      allParents: a list of dictionaries each representing a node in the tree that is a parent

  """
  allParents = []
  for node in tree:
    for implication in implications:
      if removeKey(node, "parents") == implication[0]:
        allParents.append(implication[1])

  return(allParents)

def findLeaves(tree, allParents):
  """Returns all nodes that are leaves, i.e that are not a parent (have no children)

  Args:
    tree: a list of dictionaries each representing a node in the tree
    allParents: a list of dictionaries each representing a node in the tree that is a parent

  Returns:
    leaves: a list of dictionaries each representing a node in the tree that is a leaf

  """
  leaves = []
  for node in tree:
    nodeCore = removeKey(node, "parents")
    if nodeCore not in allParents and not(node["row"] == 1 and node["col"] == 1):
      leaves.append(nodeCore)

  return leaves

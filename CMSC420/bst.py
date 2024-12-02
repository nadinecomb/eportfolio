# BST Variation 1

from __future__ import annotations
import json

# The class for a particular node in the tree.
# DO NOT MODIFY!
class Node():
    def  __init__(self,
                  key        : int  = None,
                  value      : int  = None,
                  leftchild  : Node = None,
                  rightchild : Node = None):
        self.key        = key
        self.value      = value
        self.leftchild  = leftchild
        self.rightchild = rightchild

# For the tree rooted at root:
# Return the json.dumps of the list with indent=2.
# DO NOT MODIFY!
def dump(root: Node) -> str:
    def _to_dict(node) -> dict:
        return {
            "key"        : node.key,
            "value"      : node.value,
            "leftchild"  : (_to_dict(node.leftchild) if node.leftchild is not None else None),
            "rightchild" : (_to_dict(node.rightchild) if node.rightchild is not None else None)
        }
    if root == None:
        dict_repr = {}
    else:
        dict_repr = _to_dict(root)
    return json.dumps(dict_repr,indent = 2)

# For the tree rooted at root and the key and value given:
# Insert the key/value pair.
# The key is guaranteed to not be in the tree.
def insert(root: Node, key: int, value: int) -> Node:
    # Fill in code.
    if root is not None:
        if root.key < key:
            root.rightchild = insert(root.rightchild, key, value)
        else:
            root.leftchild = insert(root.leftchild, key, value)
    else:
        root = Node(key, value, None, None)
    return root

def successor(root: Node) -> Node:
    if root.leftchild is not None:
        root = successor(root.leftchild)
    return root

def is_child(root:Node):
    return root.leftchild is None and root.rightchild is None if root is not None else False
# For the tree rooted at root and the key given, delete the key.
# When replacement is necessary use the inorder successor.
def delete(root: Node, key: int) -> Node:
    # Fill in code.
    if root is None:
        return None
    if root.key < key:
        root.rightchild = delete(root.rightchild, key)
    elif root.key > key:
        root.leftchild = delete(root.leftchild, key)
    else:
        if root.leftchild is None and root.rightchild is not None:
            root = root.rightchild
        elif root.rightchild is not None:
            s = successor(root.rightchild)
            temp = delete(root, s.key) 
            root = Node(s.key, s.value, temp.leftchild, temp.rightchild)
        elif root.leftchild is not None:
            root = root.leftchild
        else: 
            root = None
        
    return root

# For the tree rooted at root and the key given:
# Calculate the list of values on the path from the root down to and including the search key node.
# The key is guaranteed to be in the tree.
# Return the json.dumps of the list with indent=2.
def search(root: Node, search_key: int) -> str:
    # Remove the next line and fill in code to construct value_list.
    value_list = []
    curr = root
    while curr is not None and curr.key != search_key:
        value_list.append(curr.value)
        if curr.key > search_key:
            curr = curr.leftchild
        elif curr.key < search_key:
            curr = curr.rightchild
    value_list.append(curr.value)
    return json.dumps(value_list,indent = 2)

def inorder(root:Node, ret):
    if root is not None:
        ret = inorder(root.leftchild, ret)
        ret.append((root.key, root.value))
        ret = inorder(root.rightchild, ret)
    return ret
    
def recrestructure(order:list):
    root = None
    if order:
        newroot = int(len(order)/2)
        root = Node(order[newroot][0], order[newroot][1], None, None)
        root.leftchild = recrestructure(order[:newroot])
        root.rightchild = recrestructure(order[newroot + 1:])
    return root
    
# Restructure the tree..
def restructure(root: Node):
    # Remove the next line and fill in code to restructure and assign the newroot.
    order = inorder(root, [])
    newroot = int(len(order)/2)
    new = Node(order[newroot][0], order[newroot][1], None, None)
    newleft = recrestructure(order[:newroot])
    newright = recrestructure(order[newroot + 1:])
    return Node(new.key, new.value, newleft, newright)

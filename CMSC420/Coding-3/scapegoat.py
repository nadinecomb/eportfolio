from __future__ import annotations
import json
import math
from typing import List


# Node Class
# You may make minor modifications.

class Node():
    def  __init__(self,
                  key        = None,
                  value      = None,
                  leftchild  = None,
                  rightchild = None,
                  parent = None):
        self.key        = key
        self.value      = value
        self.leftchild  = leftchild
        self.rightchild = rightchild
        self.parent = parent

# Scapegoat Tree Class.
# DO NOT MODIFY.
class SGtree():
    def  __init__(self,
                  a    : int  = None,
                  b    : int  = None,
                  m    : int  = None,
                  n    : int  = None,
                  root : Node = None,
                  height: int = None):
        self.m     = 0
        self.n     = 0
        self.a     = a
        self.b     = b
        self.root  = None
        self.last = 0

    # For the tree rooted at root, dump the tree to stringified JSON object and return.
    def dump(self) -> str:
        def _to_dict(node) -> dict:
            pk = None
            if node.parent is not None:
                pk = node.parent.key
            return {
                "k": node.key,
                "v": node.value,
                "l": (_to_dict(node.leftchild)  if node.leftchild  is not None else None),
                "r": (_to_dict(node.rightchild) if node.rightchild is not None else None)
            }
        if self.root == None:
            dict_repr = {}
        else:
            dict_repr = _to_dict(self.root)
        return json.dumps(dict_repr,indent=2)
    
    #insert the key,value pair into the traee as per 
    #scapegoat tree rules, the key is not guaranteed to
    #be in the tree
    #insert as with check if rebuild is needed
    #update m and n
    def inorder(self, node):
        list = []
        if node is not None:
            list += self.inorder(node.leftchild)
            list += [node]
            list += self.inorder(node.rightchild)
        return list

    def is_scapegoat(self, node):
        rl = len(self.inorder(node.rightchild))
        ll = len(self.inorder(node.leftchild))
        tot = rl + ll + 1
        return (float(rl)/float(tot) > float(self.a)/float(self.b) or float(ll)/float(tot) > float(self.a)/float(self.b))

    def rebuild(self, list, d):
        m = len(list)//2
        node = None
        if(len(list) != 0):
            node = Node(list[m].key, list[m].value)
            node.leftchild = self.rebuild(list[0:m], d + 1)
            node.rightchild = self.rebuild(list[m+1:], d + 1)
        return node

    def rec_ins(self, d, key, value, node):
        rebuilt = False
        if(node is None): #insert the node
            self.n += 1
            if (self.m < self.n):
                self.m = self.n
            self.last = d
            node = Node(key, value)
        elif(node.key == key):
            node.value = value
        elif(node.key > key):
            node.leftchild,rebuilt = self.rec_ins(d + 1, key, value, node.leftchild)
            if (self.last > math.log(self.n,float(self.b)/float(self.a)) and self.is_scapegoat(node) and 
                    rebuilt == False):
                rebuilt = True
                node = self.rebuild(self.inorder(node), d)
        else: 
            node.rightchild,rebuilt = self.rec_ins(d + 1, key, value, node.rightchild)
            if (self.last > math.log(self.n,float(self.b)/float(self.a)) and self.is_scapegoat(node) and 
                    rebuilt == False):
                rebuilt = True
                node = self.rebuild(self.inorder(node), d)
        return node,rebuilt

    def insert(self, key: int, value: str):
        # Fill in the details.
        if (self.root is None or self.root.key == key):
            if(self.root is None):
                self.root = Node(key, value)
                self.m += 1
                self.n += 1
            else:
                self.root.value = value
        else:
            
            self.root, rebuilt = self.rec_ins(0, key, value, self.root)
        return self.root
            
    #delete the key, value pair from the tree and rebalance as per 
    #scapegoat tree rules. the key is guaranteed to be in the tree
    def successor(self, node):
        if node is None:
            return None
        else:
            ret = self.successor(node.leftchild)
            if ret is None:
                ret = node
        return ret

    def rec_del(self, key, node, change):
        if(node is not None):
            if(node.key == key):
                new_node = self.successor(node.rightchild)
                if new_node is None and node.leftchild is not None:
                    node = node.leftchild
                elif new_node is None:
                    node = None
                elif node.leftchild is None:
                    node = node.rightchild
                else:
                    old = node
                    node = new_node
                    node.rightchild = self.rec_del(node.key, old.rightchild, False)
                    node.leftchild = old.leftchild
                if(change):
                    self.n -= 1
            elif(node.key > key):
                node.leftchild = self.rec_del(key, node.leftchild, change)
            else:
                node.rightchild = self.rec_del(key, node.rightchild, change)
        return node

    def delete(self, key: int):
        # Fill in the details.
        if(self.root is not None):
            self.root = self.rec_del(key, self.root, True)
            if(self.n < float(self.a)/float(self.b) * float(self.m)):
                self.root = self.rebuild(self.inorder(self.root), 0)
                self.m = self.n

    #calculate the list of values on the path from the root to the search key
    #including the value associated to the search key.
    #the key is guaranteed to be in the tree
    def rec_search(self, search_key, node) -> list[str]:
        if(node is None):
            return []
        else:
            if(search_key == node.key):
                return [node.value] 
            elif(search_key < node.key):
                return [node.value] + self.rec_search(search_key, node.leftchild)
            else:
                return [node.value] + self.rec_search(search_key, node.rightchild)
    def search(self, search_key: int) -> str:
        ret = "["
        list = self.rec_search(search_key, self.root)
        for i in range(len(list)):
            ret += "\""
            ret += list[i] 
            ret += "\""
            if(i != len(list) - 1):
                ret += ", "
            else:
                ret += "]"
        return ret

from __future__ import annotations
import json
import math
from typing import List

verbose = False

# DO NOT MODIFY!
class Node():
    def  __init__(self,
                  key      : int,
                  value    : str,
                  toplevel : int,
                  pointers : List[Node] = None):
        self.key      = key
        self.value    = value
        self.toplevel = toplevel
        self.pointers = pointers

# DO NOT MODIFY!
class SkipList():
    def  __init__(self,
                  maxlevel : int = None,
                  nodecount: int = None,
                  headnode : Node = None,
                  tailnode : Node = None):
        self.maxlevel = maxlevel
        self.nodecount = nodecount
        self.headnode  = headnode
        self.tailnode  = tailnode

    # DO NOT MODIFY!
    # Return a reasonable-looking json.dumps of the object with indent=2.
    # We create an list of nodes,
    # For each node we show the key, the value, and the list of pointers and the key each points to.
    def dump(self) -> str:
        currentNode = self.headnode
        nodeList = []
        while currentNode is not self.tailnode:
            pointerList = str([n.key for n in currentNode.pointers])
            nodeList.append({'key':currentNode.key,'value':currentNode.value,'pointers':pointerList})
            currentNode = currentNode.pointers[0]
        pointerList = str([None for n in currentNode.pointers])
        nodeList.append({'key':currentNode.key,'value':currentNode.value,'pointers':pointerList})
        return json.dumps(nodeList,indent = 2)

    # DO NOT MODIFY!
    # Creates a pretty rendition of a skip list.
    # It's vertical rather than horizontal in order to manage different lengths more gracefully.
    # This will never be part of a test but you can put "pretty" as a single line in your tracefile
    # to see what the result looks like.
    def pretty(self) -> str:
        currentNode = self.headnode
        longest = 0
        while currentNode != None:
            if len(str(currentNode.key)) > longest:
                longest = len(str(currentNode.key))
            currentNode = currentNode.pointers[0]
        longest = longest + 2
        pretty = ''
        currentNode = self.headnode
        while currentNode != None:
            lineT = 'Key = ' + str(currentNode.key) + ', Value = ' + str(currentNode.value)
            lineB = ''
            for p in currentNode.pointers:
                if p is not None:
                    lineB = lineB + ('('+str(p.key)+')').ljust(longest)
                else:
                    lineB = lineB + ''.ljust(longest)
            pretty = pretty + lineT
            if currentNode != self.tailnode:
                pretty = pretty + "\n"
                pretty = pretty + lineB + "\n"
                pretty = pretty + "\n"
            currentNode = currentNode.pointers[0]
        return(pretty)

    # DO NOT MODIFY!
    # Initialize a skip list.
    # This constructs the headnode and tailnode each with maximum level maxlevel.
    # Headnode has key -inf, and pointers point to tailnode.
    # Tailnode has key inf, and pointers point to None.
    # Both have value None.
    def initialize(self,maxlevel):
        pointers = [None] * (1+maxlevel)
        tailnode = Node(key = float('inf'),value = None,toplevel = maxlevel,pointers = pointers)
        pointers = [tailnode] * (maxlevel+1)
        headnode = Node(key = float('-inf'),value = None, toplevel = maxlevel,pointers = pointers)
        self.headnode = headnode
        self.tailnode = tailnode
        self.maxlevel = maxlevel
        self.nodecount = 0
    #note that the expected top level is 1+lg(n)
    # Create and insert a node with the given key, value, and toplevel.
    # The key is guaranteed to not be in the skiplist.
    # Check if we need to rebuild and do so if needed.
    def level(self, index):
        i = self.maxlevel
        while(i > 0):
            if(index % math.pow(2, i) == 0):
                return i
            else:
                i -= 1

        return 0
    def insert(self,key,value,toplevel):
        self.nodecount += 1
        i = self.maxlevel
        curr = self.headnode
        while(i >= 0):
            if(curr.pointers[i].key > key): #overshoot
                i-=1
            else: #not an overshoot, follow the pointer
                curr = curr.pointers[i]
        #create the node
        i = 0
        prev_node = curr
        pointers = [None] * (toplevel + 1)
        while(i <= toplevel and prev_node.toplevel >= i):
            pointers[i] = prev_node.pointers[i]
            i += 1
        if(i <= toplevel):
            prev_node = prev_node.pointers[i - 1]
            while(i <= toplevel):
                if(prev_node.toplevel >= i):
                    pointers[i] = prev_node
                    i += 1
                else:
                    prev_node = prev_node.pointers[i-1]
        new_node = Node(key, value, toplevel, pointers)
        i = toplevel
        curr = self.headnode
        while(i >= 0):
            if(curr.pointers[i].key > key): #overshoot and set the next pointer to the new node
                curr.pointers[i] = new_node
                i-=1
            else: #not an overshoot, follow the pointer
                curr = curr.pointers[i]
        # if lg(n) + 1 > max_level -> rebuild the list
        curr  = self.headnode
        if(math.log(self.nodecount, 2) + 1 > self.maxlevel):
            num = self.nodecount
            self.initialize(self.maxlevel * 2)
            index = 1
            while(index <= num):
                new_node = curr.pointers[0]
                self.insert(new_node.key, new_node.value, self.level(index));
                curr = curr.pointers[0]
                index += 1
            self.nodecount = num

    # Delete node with the given key.
    # The key is guaranteed to be in the skiplist.
    def delete(self,key):
        lst = []
        self.nodecount -= 1
        i = self.maxlevel
        curr = self.headnode
        while(i >= 0):
            if(curr.pointers[i].key > key): #overshoot
                i-=1
            elif(curr.pointers[i].key == key):
                lst.append(curr)
                i-=1
            else: #not an overshoot, follow the pointer
                curr = curr.pointers[i]
        curr = curr.pointers[0]
        j = curr.toplevel
        for i in range(len(lst)):
            lst[i].pointers[j] = curr.pointers[j]
            j -= 1
    # Search for the given key.
    # Construct a list of all the keys in all the nodes visited during the search.
    # Append the value associated to the given key to this list.
    def search(self,key) -> str:
        A = []
        i = self.maxlevel
        curr = self.headnode
        while(i >= 0):
            if curr.key not in A:
                A.append(curr.key)
            if(curr.pointers[i].key > key): #overshoot
                i-=1
            else: #not an overshoot, follow the pointer
                curr = curr.pointers[i]
        A.append(curr.value)

        return json.dumps(A,indent = 2)

from __future__ import annotations
import json
import math
from typing import List

# Datum class.
# DO NOT MODIFY.
class Datum():
    def __init__(self,
                 coords : tuple[int],
                 code   : str):
        self.coords = coords
        self.code   = code
    def to_json(self) -> str:
        dict_repr = {'code':self.code,'coords':self.coords}
        return(dict_repr)

# Internal node class.
# DO NOT MODIFY.
class NodeInternal():
    def  __init__(self,
                  splitindex : int,
                  splitvalue : float,
                  leftchild,
                  rightchild):
        self.splitindex = splitindex
        self.splitvalue = splitvalue
        self.leftchild  = leftchild
        self.rightchild = rightchild

# Leaf node class.
# DO NOT MODIFY.
class NodeLeaf():
    def  __init__(self,
                  data : List[Datum]):
        self.data = data

# KD tree class.
class KDtree():
    def  __init__(self,
                  splitmethod : str,
                  k           : int,
                  m           : int,
                  root        : NodeLeaf = None):
        self.k    = k
        self.m    = m
        self.splitmethod = splitmethod
        self.root = root

    # For the tree rooted at root, dump the tree to stringified JSON object and return.
    # DO NOT MODIFY.
    def dump(self) -> str:
        def _to_dict(node) -> dict:
            if isinstance(node,NodeLeaf):
                return {
                    "p": str([{'coords': datum.coords,'code': datum.code} for datum in node.data])
                }
            else:
                return {
                    "splitindex": node.splitindex,
                    "splitvalue": node.splitvalue,
                    "l": (_to_dict(node.leftchild)  if node.leftchild  is not None else None),
                    "r": (_to_dict(node.rightchild) if node.rightchild is not None else None)
                }
        if self.root is None:
            dict_repr = {}
        else:
            dict_repr = _to_dict(self.root)
        return json.dumps(dict_repr,indent=2)

    # Insert the Datum with the given code and coords into the tree.
    # The Datum with the given coords is guaranteed to not be in the tree.
    def spread(self, lst):
        maxs = 0
        maxi = -1
        lists = []
        c = int(len(lst)/2)
        for i in range(len(lst)):
            lists.append(lst[i].coords)
        newlist = lambda y : list(map(lambda x: x[y], lists))
        for i in range(self.k):
            spread = max(newlist(i)) - min(newlist(i))
            if( spread > maxs):
                maxi =i
                maxs = spread
        lst.sort(key = lambda x: x.coords[maxi])
        return maxi, lst[:c], lst[c:]

    def spread_ins(self, node, point, code, idx):
        if node is None:
            node = NodeLeaf([Datum(point, code)])
        elif type(node) == NodeLeaf:
            node.data.append(Datum(point, code))
            if len(node.data) > self.m:
                c = (len(node.data))//2

                if self.splitmethod == "spread":
                    index,ll,rl = self.spread(node.data)
                    if len(node.data) % 2 == 1:
                        split = rl[0].coords[index]
                    else:
                        split = (ll[c-1].coords[index] + rl[0].coords[index])/2
                    node = NodeInternal(index, float(split), NodeLeaf(ll), NodeLeaf(rl))
                else:
                    index = idx % self.k
                    node.data.sort(key = lambda x: x.coords[index])
                    if len(node.data) % 2 == 1:
                        split = node.data[c].coords[index]
                    else:
                        split = (node.data[c].coords[index] + node.data[c - 1].coords[index])/2
                    node = NodeInternal(index, float(split),NodeLeaf(node.data[:c]), NodeLeaf(node.data[c:]))
        else:
            if node.splitvalue > point[node.splitindex]:
                node.leftchild = self.spread_ins(node.leftchild, point, code, node.splitindex + 1)
            else:
                node.rightchild = self.spread_ins(node.rightchild, point, code, node.splitindex + 1)
        return node

    def insert(self,point:tuple[int],code:str):
        self.root = self.spread_ins(self.root, point, code, 0)

    # Delete the Datum with the given point from the tree.
    # The Datum with the given point is guaranteed to be in the tree.
    def rec_del(self, node, point):
        if type(node) == NodeLeaf:
            lst = list(map(lambda x: x.coords, node.data))
            node.data.pop(lst.index(point))
        else:
            if node.splitvalue > point[node.splitindex]:
                node.leftchild = self.rec_del(node.leftchild, point)
                if type(node.leftchild) == NodeLeaf and len(node.leftchild.data) == 0:
                    node = node.rightchild
            else:
                node.rightchild = self.rec_del(node.rightchild, point)
                if type(node.rightchild) == NodeLeaf and len(node.rightchild.data) == 0:
                    node = node.leftchild
        return node

    def delete(self,point:tuple[int]):
        self.root = self.rec_del(self.root, point)

    # Find the k nearest neighbors to the point.
    def closest(self, node):
        #create a list of all nodes in the current subtree
        if(node is not None):
            if(type(node) == NodeInternal):
                left = self.closest(node.leftchild)
                right = self.closest(node.rightchild)
                return left + right
            else:
                return node.data
        else:
           return 0,0
    def bounding_box(self, points, index):
        newlist = lambda y : list(map(lambda x: x.coords[y], points))
        return (min(newlist(index)), max(newlist(index)))
    def rec_knn(self, node, k, point, lst):
        #note: k is the number of elements that can be in the knn list
        #note: knnlist will be a list of tuples of points with distances
        if(type(node) == NodeInternal):
            rl = self.closest(node.rightchild)
            ll = self.closest(node.leftchild)
            lsts = (ll,rl)
            dist = [0,0]
            numcheckedr, numcheckedl = (0,0)
            for j in range(2):
                for i in range(self.k):
                    min, max = self.bounding_box(lsts[j], i)
                    if point[i] < min:
                        dist[j] += (point[i] - min) ** 2
                    elif point[i] > max:
                        dist[j] += (point[i] - max) ** 2
            if(dist[0] <= dist[1] and (k > len(lst) or dist[0] <= lst[-1][1])):
                numcheckedl, lst = self.rec_knn(node.leftchild, k, point, lst)
                if(lst[-1][1] >= dist[1] or k > len(lst)):
                    numcheckedr, lst = self.rec_knn(node.rightchild, k, point, lst)
            elif(dist[0] > dist[1] and (k > len(lst) or dist[1] <= lst[-1][1])):
                numcheckedr, lst = self.rec_knn(node.rightchild, k, point, lst)
                if(lst[-1][1] >= dist[0] or k > len(lst)):
                    numcheckedl, lst = self.rec_knn(node.leftchild, k, point, lst)
            leaveschecked = numcheckedl + numcheckedr
            return leaveschecked, lst
        else:
            if len(lst) == 0:
                for j in range(len(node.data)):
                    dist = 0
                    for i in range(self.k):
                        dist += (point[i] - node.data[j].coords[i]) ** 2
                    lst.append((node.data[j], dist))
                lst.sort(key = lambda x: (x[1], x[0].code))
                lst = lst[:k]
            else:
                j = len(node.data) - 1
                while(j >= 0):
                    dist = 0
                    for i in range(self.k):
                        dist += (point[i] - node.data[j].coords[i]) ** 2
                    if(dist <= lst[-1][1] or len(lst) < k):
                        newnode = node.data[j]
                        if(dist == lst[-1][1] and len(lst) >= k):
                            if(lst[len(lst) - 1][0].code > newnode.code):
                                lst.pop()
                            else:
                                newnode = lst[-1][0]
                                lst.pop()
                        elif(len(lst) >= k):
                            lst.pop() 
                        lst.append((newnode, dist))
                        lst.sort(key = lambda x: (x[1], x[0].code))
                    j -= 1
            return 1, lst
    def knn(self,k:int,point:tuple[int]) -> str:
        # Use the strategy discussed in class and in the notes.
        # The list should be a list of elements of type Datum.
        # While recursing, count the number of leaf nodes visited while you construct the list.
        # The following lines should be replaced by code that does the job.
        leaveschecked, knnlist = self.rec_knn(self.root, k, point, [])
        knnlist = list(map(lambda x: x[0], knnlist))
        # The following return line can probably be left alone unless you make changes in variable names.
        return(json.dumps({"leaveschecked":leaveschecked,"points":[datum.to_json() for datum in knnlist]},indent=2))

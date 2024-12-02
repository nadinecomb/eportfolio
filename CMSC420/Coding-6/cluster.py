from __future__ import annotations
import json
import math
from typing import List
import numpy as np

class Graph():
    def  __init__(self,
            nodecount : None):
        self.nodecount = nodecount
        # IMPORTANT!!!
        # Replace the next line so the Laplacian is a nodecount x nodecount array of zeros.
        # You will need to do this in order for the code to run!
        self.laplacian = np.zeros((nodecount, nodecount))

    # Add an edge to the Laplacian matrix.
    # An edge is a pair [x,y].
    def addedge(self,edge):
        # Your code goes here.
        # Nothing to return.
        A = np.zeros((self.nodecount, self.nodecount))
        D = np.zeros((self.nodecount, self.nodecount))
        A[edge[0], edge[1]] = 1
        A[edge[1], edge[0]] = 1
        for i in range(self.nodecount):
            for j in range(self.nodecount):
                D[i,i] += A[i, j] 
        self.laplacian = D - A + self.laplacian


    # Don't change this - no need.
    def laplacianmatrix(self) -> np.array:
        return self.laplacian

    # Calculate the Fiedler vector and return it.
    # You can use the default one from np.linalg.eig
    # but make sure the first entry is positive.
    # If not, negate the whole thing.
    def fiedlervector(self) -> np.array:
        # Replace this next line with your code.
        eigval, eigvect = np.linalg.eig(self.laplacian)
        fvec = np.zeros(self.nodecount)
        index = 0
        min = max(eigval)
        for i in range(1, len(eigval)):
            if(eigval[i] < min and eigval[i].round(decimals=8) > 0):
                min = eigval[i]
                index = i
        if(np.iscomplex(eigvect).any()):
            fvec = fvec.astype(complex)
        for i in range(self.nodecount):
            fvec[i] = eigvect[i, index]
        if(fvec[0] < 0):
            fvec = np.negative(fvec)
        # Return
        return fvec.round(decimals=8)

    # Cluster the nodes.
    # You should return a list of two lists.
    # The first list contains all the indices with nonnegative (positive and 0) Fiedler vector entry.
    # The second list contains all the indices with negative Fiedler vector entry.

    def clustersign(self):
        # Replace the next two lines with your code.
        pind = []
        nind = []
        A = self.fiedlervector()
        for i in range(int(self.nodecount)):
            if(A[i] < 0):
                nind.append(i)
            else:
                pind.append(i)
        # Return
        return([pind,nind])

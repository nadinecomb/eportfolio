from ucimlrepo import fetch_ucirepo
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# instructions to run: 
# pip install ucimlrepo
# pip install pandas
# pip install numpy
# python3 q2.py

# fetch dataset
wine = fetch_ucirepo(id=109)
# data (as pandas dataframes)
# features are x
features = wine.data.features
# targets are the classifications
targets = wine.data.targets
# prints the features
print(f'size of features: {len(features)}')
print(f'does the wine dataset have missing values? {wine.metadata.has_missing_values}')

# retrieve the covariance matrix, evect, and evals using np
features = features/np.mean(features)
C = features.cov()
eval, evect = np.linalg.eig(C)

#sort the evals in decreasing order
idx = np.argsort(eval)[::-1]
eval = eval[idx]
evect = evect[:, idx]

print(f'covariance matrix: {C.to_string(index=False, header=False)}')
print(f'eigenvalues: {eval}')

pc1 = evect[0]
pc2 = evect[1]
pc3 = evect[2]

print(f'principal component 1: {pc1}')
print(f'principal component 2: {pc2}')
print(f'principal component 3: {pc3}')

onedim = pc1
twodim = np.vstack((pc1, pc2))
threedim = np.vstack((pc1, pc2, pc3))

fig = plt.figure()
one = fig.add_subplot()
one.scatter(onedim, np.zeros_like(onedim))
one.set_xlabel('x1')
one.set_ylabel('0')
one.set_title('1-d projection of data')

plt.savefig("q2_output_1.png")
fig = plt.figure()
two = fig.add_subplot()
two.scatter(twodim[0], twodim[1])
two.set_xlabel('x1')
two.set_ylabel('x2')
two.set_title('2-d projection of data')

plt.savefig("q2_output_2.png")
fig = plt.figure()
three = fig.add_subplot(projection='3d')
three.scatter3D(threedim[0], threedim[1], threedim[2])
three.set_xlabel('x1')
three.set_ylabel('x2')
three.set_zlabel('x3')
three.set_title('3-d projection of data')

plt.savefig("q2_output_3.png")

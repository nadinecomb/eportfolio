from sklearn.datasets import fetch_openml
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
import warnings
from sklearn.exceptions import ConvergenceWarning
warnings.simplefilter("ignore", category=ConvergenceWarning)

mnist = fetch_openml('mnist_784')

#separate features (x) and targets/labels (y)
features = mnist.data.to_numpy().astype(int)
targets = mnist.target.to_numpy().astype(int)

#split training and validation data to be 60k/10k split
x_test, x_train, y_test, y_train = train_test_split(features, targets, test_size=float(1/7))

# graph number of iterations v.s. accuracy for training and test data up to 50 iterations
fig = plt.figure()
test_plot = fig.add_subplot(2, 2, 1)
test_plot_loss = fig.add_subplot(2, 2, 2)
train_plot = fig.add_subplot(2, 2, 3)
train_plot_loss = fig.add_subplot(2, 2, 4)
for i in (1, 6, 10, 20, 50, 100, 200, 300):
    # max_iter = i,learning_rate_init=0.001, uses adam 
    mlp = MLPClassifier(activation='logistic', hidden_layer_sizes=(300,100), max_iter=i)
    mlp.fit(x_train, y_train)
    # get predicted classifications for validation and test data, and check for accuracy
    y_pred = mlp.predict(x_test) 
    accuracy = accuracy_score(y_test, y_pred)
    loss = np.sum((y_pred - y_test)**2)
    test_plot.scatter(i, accuracy)
    test_plot_loss.scatter(i, loss)

    y_pred = mlp.predict(x_train) 
    accuracy = accuracy_score(y_train, y_pred)
    loss = np.sum((y_pred - y_train)**2)
    train_plot.scatter(i, accuracy)
    train_plot_loss.scatter(i, loss)

train_plot.set_title('Accuracy v.s. Iterations for Training Data')
test_plot.set_title('Accuracy v.s. Iterations for Test Data')
train_plot_loss.set_title('Loss v.s. Iterations for Training Data')
test_plot_loss.set_title('Loss v.s. Iterations for Test Data')

train_plot.set_xlabel('Iteration')
test_plot.set_xlabel('Iteration')
train_plot_loss.set_xlabel('Iteration')
test_plot_loss.set_xlabel('Iteration')

train_plot.set_ylabel('Accuracy')
test_plot.set_ylabel('Accuracy')
train_plot_loss.set_ylabel('Loss')
test_plot_loss.set_ylabel('Loss')

plt.gcf().set_size_inches(20, 20)
plt.savefig('q4.png', dpi = 200)

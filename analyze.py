#!/usr/bin/python3.4
# Generates files with feature featuretors for a specific position
from sklearn import linear_model
import numpy as np

def linear_regression(filename):
    feature_f = open(filename, 'r')

    features = []
    labels = []
    for line in feature_f:
        vec = line.split()
        features.append([float(x) for x in vec[0:-1]])
        labels.append(float(vec[-1]))

    train = features[0:-len(features)//5]
    train_l = labels[0:-len(features)//5]
    test = features[-len(labels)//5:]
    test_l = labels[-len(labels)//5:]


    model = linear_model.LinearRegression()
    model.fit(train, train_l)
    print(np.mean(abs(model.predict(test) - test_l)))
    print(model.score(test, test_l))

if __name__ == "__main__":
    # Input file(s)
    for filename in ['qb.txt']:
    	linear_regression(filename)

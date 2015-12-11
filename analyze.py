#!/usr/bin/python3.4
# Generates files with feature features for a specific position
import itertools
from random import shuffle
from sklearn import linear_model
from sklearn.feature_selection import RFECV
from sklearn.svm import SVR
import numpy as np

def feature_selection(data, label):
    mask = [ True, True, False, True, True, True, False, True, False, True, False, False, False, True ,False ,False ,True, False ,False ,False]
    #selector = RFECV(svm_classifier, step=1, cv=2)
    #selector = selector.fit(train, train_l)
    new_data = []
    for feature in data:
        new_data.append([value for (value, m) in zip(feature, mask) if m])
    return new_data


def analyze(data, label, num_folds):
    # Partition data into folds
    n = len(data) // num_folds
    data_folds = [data[i:i+n] for i in range(0, len(data), n)]
    label_folds = [label[i:i+n] for i in range(0, len(label), n)]

    lin_reg_error = 0
    
    cs = [c/10 for c in range(150, 300, 10)]
    svm_error = [0] * len(cs)
    svm_std = [0] * len(cs)
    for i in range(0, num_folds):
        test_data = data_folds[i]
        test_label = label_folds[i]
        train_data = []
        train_label = []
        for j in range(num_folds):
            if i != j:
                train_data += data_folds[i]
                train_label += label_folds[i]

        model = linear_model.LinearRegression()
        model.fit(train_data, train_label)
        lin_reg_error += np.mean(abs(model.predict(test_data) - test_label))

        for i in range(len(cs)):
            svm_classifier = SVR(C=cs[i])
            svm_classifier.fit(train_data, train_label)
            svm_error[i] += np.mean(abs(svm_classifier.predict(test_data) - test_label))
            svm_std[i] += np.std(abs(svm_classifier.predict(test_data) - test_label))

    print("Linear Regression avg. error: " + str(lin_reg_error/num_folds))
    for i in range(len(svm_error)):
        print("Support Vector Machine avg. error: " + str(svm_error[i]/num_folds))
        print("Support Vector Machine error std. deviation: " + str(svm_std[i]/num_folds))


if __name__ == "__main__":
    num_folds = 5

    # Input file(s)
    for filename in ['qb.txt']:
        feature_f = open(filename, 'r')
        rows = [[float(x) for x in line.split()] for line in feature_f]
        shuffle(rows)
        data = [row[0:-1] for row in rows]
        label = [row[-1] for row in rows]
        new_data = feature_selection(data, label)
        analyze(new_data, label, num_folds)
        feature_f.close()

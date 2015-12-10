#!/usr/bin/python3.4
# Generates files with feature features for a specific position
from sklearn import linear_model
from sklearn.feature_selection import RFECV
from sklearn.svm import SVR
import numpy as np

def linear_regression(filename):
    feature_f = open(filename, 'r')

    features = []
    labels = []
    mask = [ True, True, False, True, True, True, False, True, False, True, False, False, False, True ,False ,False ,True, False ,False ,False]
    for line in feature_f:
        vec = line.split()
        features.append([float(x) for x in vec[0:-1]])
        labels.append(float(vec[-1]))

    new_data = []

    for feature in features:
        new_data.append( [value for (value, m) in zip(feature, mask) if m])

    num_folds = 5
    data_folds = partition_into_folds(new_data, num_folds)
    label_folds = partition_into_folds(labels, num_folds)

    lin_reg_error = 0
    svm_error = 0

    for i in range(0,num_folds):
        train_data = []
        train_label = []
        test_data = []
        test_label = []
        for j in range(num_folds):
            if i != j:
                train_data += data_folds[i]
                train_label += label_folds[i]
            else:
                test_data += data_folds[i]
                test_label += label_folds[i]

        model = linear_model.LinearRegression()
        model.fit(train_data, train_label)
        lin_reg_error += np.mean(abs(model.predict(test_data) - test_label))

        svm_classifier = SVR()
        svm_classifier.fit(train_data, train_label)
        svm_error += np.mean(abs(svm_classifier.predict(test_data) - test_label))

    print("Linear Regression avg. error: " + str(lin_reg_error/num_folds))
    print("Support Vector Machine avg. error: " + str(svm_error/num_folds))
    #selector = RFECV(svm_classifier, step=1, cv=5)
    #selector = selector.fit(train, train_l)
    #print(selector.support_)
    #print(selector.ranking_)


def partition_into_folds(data, num_folds):
    folds = []
    for i in range(num_folds):
        fold = []
        for j in range(i,len(data),num_folds):
            fold.append(data[j])
        folds.append(fold)
    return folds


if __name__ == "__main__":
    # Input file(s)
    for filename in ['qb.txt']:
    	linear_regression(filename)

#!/usr/bin/python3.4
# Generates files with feature features for a specific position
from random import shuffle
from sklearn import linear_model
from sklearn.feature_selection import RFECV
from sklearn.svm import SVR
import numpy as np
import matplotlib.pyplot as plt

def feature_selection(data, label):
    mask = [ True, True, False, True, True, True, False, True, False, True, False, False, False, True ,False ,False ,True, False ,False ,False]
    svm_classifier = SVR(kernel="linear")
    selector = RFECV(svm_classifier, step=1, cv=5)
    selector = selector.fit(data, label)
    mask = selector.support_
    print(mask)
    print(selector.ranking_)
    new_data = []
    for feature in data:
        new_data.append([value for (value, m) in zip(feature, mask) if m])
    return new_data

def select_features(data, mask):
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
    
    cs = [4**c for c in range(-10, 0, 1)]
    svm_error = [0] * len(cs)
    svm_std = [0] * len(cs)
    # for i in range(0, num_folds):
    #     test_data = data_folds[i]
    #     test_label = label_folds[i]
    #     train_data = []
    #     train_label = []
    #     for j in range(num_folds):
    #         if i != j:
    #             train_data += data_folds[j]
    #             train_label += label_folds[j]

    # model = linear_model.LinearRegression()
    # model.fit(data, label)
    # return model
        # lin_reg_error += np.mean(abs(model.predict(test_data) - test_label))
        #
        # for i2 in range(len(cs)):
        #     svm_classifier = SVR(gamma=cs[i2])
        #     svm_classifier.fit(train_data, train_label)
        #     svm_error[i2] += np.mean(abs(svm_classifier.predict(test_data) - test_label))
        #     svm_std[i2] += np.std(abs(svm_classifier.predict(test_data) - test_label))

    svm_c = SVR(gamma=4**-7)
    svm_c.fit(data, label)
    return svm_c



    # print("Linear Regression avg. error: " + str(lin_reg_error/num_folds))
    # for i in range(len(svm_error)):
    #     print(str(svm_error[i]/num_folds))
    #     # print("Support Vector Machine error std. deviation: " + str(svm_std[i]/num_folds))


if __name__ == "__main__":
    num_folds = 5

    # Input file(s)
    feature_f = open('qbtrain.txt', 'r')
    rows = [[float(x) for x in line.split()] for line in feature_f]
    shuffle(rows)
    data = [row[0:-2] for row in rows]
    label = [row[-2] for row in rows]
    mask = [ True, False  ,True  ,True  ,True  ,True  ,True ,False  ,True  ,True  ,True  ,True,
 False  ,True  ,True  ,True ,False ,False ,False ,False  ,True ,False  ,True  ,True,
  True  ,True]
    new_data = select_features(data, mask)
    model = analyze(data, label, num_folds)

    # Get test data from file
    test_data_file = open('qbtest.txt', 'r')
    rows = [[float(x) for x in line.split()] for line in test_data_file if line.split()[-1] != '-99']
    test_data = [row[0:-2] for row in rows]
    test_label = [row[-2] for row in rows]
    espn_label = [row[-1] for row in rows]

    # test_data = select_features(test_data, mask)
    predictions = model.predict(test_data)
    prediction_error = abs(predictions - test_label)
    espn_error = abs(np.asarray(espn_label) - test_label)
    print(np.mean(prediction_error))
    print('espn error' + str(np.mean(espn_error)))
    plt.plot(*zip([test_label, espn_error]), marker='o', color='r', ls='')
    plt.ylabel('Absolute error')
    plt.xlabel('True label')
    plt.title('Running Back true label vs. absolute error')
    plt.show()

    feature_f.close()
    # test_data_file.close()

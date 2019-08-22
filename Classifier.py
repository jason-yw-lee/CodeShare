import numpy as np



import matplotlib.pyplot as plt
import seaborn as sns
import math



import pandas as pd



import sklearn
from sklearn import neighbors
from sklearn import svm
from sklearn import gaussian_process
from sklearn import tree
from sklearn import ensemble
from sklearn import naive_bayes
from sklearn import discriminant_analysis
from xgboost.sklearn import XGBClassifier
from xgboost import plot_tree
from sklearn.model_selection import GridSearchCV

import datetime

class Classifier:
	def __init__(self, X, y):
		self.X = np.array(X)
		self.y = np.array(y)

		# Data variables
		self.N = len(self.y)  # Total number of records
		self.n = math.floor(len(self.y) * .67)  # Number of records for training data
		self.r = len(np.unique(self.y))  # Number of unique Classes in data

		# Shuffle data
		self.shuffle = np.array(range(self.N))
		np.random.shuffle(self.shuffle)
		self.X_shuffle = []
		self.y_shuffle = []
		for s in self.shuffle:
			self.X_shuffle.append(self.X[s])
			self.y_shuffle.append(self.y[s])

		self.X_shuffle = np.array(self.X_shuffle)
		self.y_shuffle = np.array(self.y_shuffle)

		# Training data
		self.X_train = self.X_shuffle[:self.n]
		self.y_train = self.y_shuffle[:self.n]

		# Testing data
		self.X_test = self.X_shuffle[self.n:]
		self.y_test = self.y_shuffle[self.n:]

		# Models
		### XGB
		self.clfXgb = XGBClassifier(objective='binary:logistic')

		self.paramXgb = {
			            'nthread':[4], #when use hyperthread, xgboost may become slower
			            'objective':['binary:logistic'],
			            'learning_rate': [0.05], #so called `eta` value
			            #'max_depth': [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20],
			            'max_depth': [1,2,3,4,5],
			            'min_child_weight': [1],
			            'subsample': [1],
			            'colsample_bytree': [1],
			            'n_estimators': [100], #number of trees
			            #'missing':[-999],
			            'seed': [0]
			            }

		### Adaboost
		self.clfAdaBoost = ensemble.AdaBoostClassifier()
		self.paramAdaBoost = {
	                        'base_estimator': [tree.DecisionTreeClassifier(max_depth=1)],
	                        'n_estimators': [50,100],
	                        }

	def Diagnostics(self, clf):
		predictions = clf.predict(self.X_test)
		accuracy = sklearn.metrics.accuracy_score(predictions, self.y_test)
		cvs = sklearn.model_selection.cross_val_score(clf, self.X_shuffle, self.y_shuffle, cv=5)

		print(clf)
		print('Cross Validation Scores: ' + str(np.round(cvs, 4)))
		print('Average CV Score: ' + str(np.mean(cvs)))
		print('Testing Score: ' + str(accuracy))

		cfm = sklearn.metrics.confusion_matrix(predictions, self.y_test)
		f1, a1 = plt.subplots()
		sns.heatmap(cfm, annot=True, ax=a1)
		f1.show()
		a1.set_xlabel('Preidicted Classes')
		a1.set_ylabel('Actual classes')

		f2, a2 = plt.subplots()
		feature_importance = clf.feature_importances_
		a2.set_xticks(list(range(1,len(feature_importance)+1)))
		a2.set_xticklabels(list(range(1,len(feature_importance)+1)))
		a2.bar(list(range(1,len(feature_importance)+1)), feature_importance)

	# Instead of going through entire list, change the paramaters to use increments, then zero in in the best
	def GridSearch(self, clf, params, cv=5):
		print("Start Time: " + str(datetime.datetime.now()))
		gs = GridSearchCV(estimator = clf, param_grid = params, cv=cv)
		gs.fit(self.X_train, self.y_train)
		clf = gs.best_estimator_
		print("End Time: " + str(datetime.datetime.now()))
		return clf

	def FitXGB(self):
		clf = self.clfXgb
		params = self.paramXgb
		self.clfXgb = self.GridSearch(clf,params)
		self.Diagnostics(self.clfXgb)

	def FitAdaBoost(self):
		clf = self.clfAdaBoost
		params = self.paramAdaBoost
		self.clfAdaBoost = self.GridSearch(clf,params)
		self.Diagnostics(self.clfAdaBoost)

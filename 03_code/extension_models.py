"""Serializable natural-gradient boosting estimator with training-only target scaling."""
import numpy as np
from sklearn.base import BaseEstimator,RegressorMixin
from sklearn.tree import DecisionTreeRegressor
from ngboost import NGBRegressor
from ngboost.distns import Normal
from ngboost.scores import LogScore

class ScaledNGBoost(RegressorMixin,BaseEstimator):
 def __init__(self,max_depth=2,n_estimators=400):self.max_depth=max_depth;self.n_estimators=n_estimators
 def fit(self,X,y):
  self.y_mean_=float(np.mean(y));self.y_std_=float(np.std(y)) or 1.
  self.model_=NGBRegressor(Dist=Normal,Score=LogScore,Base=DecisionTreeRegressor(max_depth=self.max_depth,min_samples_leaf=10,random_state=42),natural_gradient=True,n_estimators=self.n_estimators,learning_rate=.03,minibatch_frac=1.,verbose=False,random_state=42)
  self.model_.fit(np.asarray(X),(np.asarray(y)-self.y_mean_)/self.y_std_);return self
 def predict(self,X):return self.model_.predict(np.asarray(X))*self.y_std_+self.y_mean_
 def distribution(self,X):
  d=self.model_.pred_dist(np.asarray(X));return np.asarray(d.loc)*self.y_std_+self.y_mean_,np.asarray(d.scale)*self.y_std_


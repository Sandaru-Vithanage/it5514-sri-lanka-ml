"""Models and finite search spaces fixed before holdout evaluation."""
import numpy as np
from scipy.optimize import minimize
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF,Matern,WhiteKernel,ConstantKernel
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.compose import TransformedTargetRegressor

def bounded_optimizer(obj_func,initial_theta,bounds):
    result=minimize(obj_func,initial_theta,method='L-BFGS-B',jac=True,bounds=bounds,options={'maxiter':80,'ftol':1e-8})
    if not result.success:
        import warnings
        warnings.warn('GPR optimizer: '+str(result.message),RuntimeWarning)
    return result.x,result.fun

def configurations():
    return {
        'Linear regression':[{}],
        'Random forest':[{'max_depth':d,'min_samples_leaf':l} for d in [6,None] for l in [2,5,10]],
        'SVR':[{'C':c,'epsilon':e} for c in [1,10,100] for e in [.05,.15]],
        'GPR':[{'kernel':k,'initial_length_scale':l} for k in ['RBF','Matern1.5','Matern2.5'] for l in [1.,5.]],
    }

def make_model(name,config,seed=42,length_multiplier=1.):
    if name=='Linear regression':return make_pipeline(StandardScaler(),LinearRegression())
    if name=='Random forest':return RandomForestRegressor(n_estimators=300,random_state=seed,n_jobs=1,**config)
    if name=='SVR':return TransformedTargetRegressor(regressor=make_pipeline(StandardScaler(),SVR(kernel='rbf',gamma='scale',**config)),transformer=StandardScaler())
    if name=='GPR':
        length=config['initial_length_scale']*length_multiplier
        if config['kernel']=='RBF':signal=RBF(length,(.1,100.))
        else:signal=Matern(length,(.1,100.),nu=1.5 if config['kernel']=='Matern1.5' else 2.5)
        kernel=ConstantKernel(1.,(.01,100.))*signal+WhiteKernel(.1,(.0001,2.))
        return make_pipeline(StandardScaler(),GaussianProcessRegressor(kernel=kernel,alpha=1e-6,normalize_y=True,optimizer=bounded_optimizer,n_restarts_optimizer=0,random_state=seed))
    raise ValueError(name)

def gpr_predict(model,X):
    return model[-1].predict(model[0].transform(X),return_std=True)

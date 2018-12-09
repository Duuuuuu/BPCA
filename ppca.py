"""
Probablistic Principal Component Analysis using the EM algorithm from Tipping & Bishop 1997.
(See http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.426.2749&rep=rep1&type=pdf)
"""

import numpy as np
from numpy.random          import randn
from numpy.random          import multivariate_normal
from numpy.linalg          import eig
from numpy.linalg          import pinv
from numpy.linalg          import multi_dot
from sklearn.exceptions    import NotFittedError

class PPCA(object):

    def __init__(self, n_dimension):
        
        # mapping from latent variables to observations: x = W z + mu + epsilon
        # where x: observation, x in R^(d)
        # q: dimension of latent space
        self._q = n_dimension 
    
    def fit(self, data, n_iteration=500, method='EM'):
        
        ####################### INITIALIZE OBSERVATIONS #######################
        # X: observations, X in R^(d*N), data assumed to be in R^(N*d)
        self._X = data.T
        # d: dimension of observations
        self._d = self._X.shape[0]
        # N: number of observations
        self._N = self._X.shape[1]
        
        if   method == 'EM':
            self._fit_EM(data, n_iteration)
        elif method == 'eig':
            self._fit_eig(data) 
        else:
            raise ValueError('unrecognized method.')
            
        # C: covariance matrix of observation, x ~ N(mu, C)
        self._C = self._sigma2 * np.eye(self._d) + np.dot(self._W, self._W.T)       
    
    def generate(self, n_sample):
        try:
            return multivariate_normal(self._mu.flatten(), self._C, n_sample)
        except:
            raise NotFittedError('This PPCA instance is not fitted yet. Call \'fit\' with appropriate arguments before using this method.')
        
    ######################## FITTING BY EM ALGORITHM ##########################
    def _fit_EM(self, data, n_iteration=500):
        
        ##################### INITIALIZE LATENT VARIABLES #####################     
        # W: linear transformation matrix, W in R^(d*q)
        self._W      = randn(self._d, self._q)
        # z: latent variable, z in R^(q)
        self._Z      = randn(self._q, self._N)
        # mu: mean of x, mu in R^(d)
        self._mu     = randn(self._d, 1)
        # epsilon: Gaussian noise, epsilon in R^(d), epsilon ~ N(0, sigma^2 I)
        self._sigma2 = np.abs(randn())
        
        for i in range(n_iteration):
            # E-step: Estimation   (omitted)
            # M-step: Maximization
            self._maximize_L()
    
    def _maximize_L(self):
        S = self._calculate_S()
        M = self._calculate_M()
        self._update_W(S, M)
        self._update_sigma2(S, M)
    
    def _update_W(self, S, M):
        temp = pinv( self._sigma2 * np.eye(self._q) \
                     + multi_dot([ pinv(M), self._W.T, S, self._W]) )
        self._W = multi_dot([ S, self._W, temp ])
    
    def _update_sigma2(self, S, M):
        temp = multi_dot([ S, self._W, pinv(M), self._W.T ])
        self._sigma2 = 1/self._d * np.trace(S - temp)
    
    ##################### FITTING BY EIGENDECOMPOSITION #######################
    def _fit_eig(self, data, n_iteration=500):
        
        self._mu = np.average(self._X, axis=1).reshape(-1, 1)
        S = self._calculate_S()
        vals, vecs = eig(S)
        ordbydom = np.argsort(vals)[::-1]
        topq_dom = ordbydom[:self._q]
        less_dom = ordbydom[self._q:]
        self._sigma2 = np.sum(vals[less_dom]) / (self._d - self._q)
        self._W = np.dot( vecs[:, topq_dom], 
                          np.sqrt(np.diag(vals[topq_dom])-self._sigma2*np.eye(self._q)) )
        # eig, sort, sigma
        return # todo
    
    ########################### UTILITY FUNCTIONS #############################
    def _calculate_S(self):
        centeredX = self._X - self._mu
        return np.dot(centeredX, centeredX.T) / self._N
    
    def _calculate_M(self):
        return self._sigma2 * np.eye(self._q) + np.dot(self._W.T, self._W)

    def _return_W(self):
        return self._W
        
        
"""PyTermStructure - Analysis"""
import numpy as np

class PCAAnalysis:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def fit(self, data):
        data = np.asarray(data)
        cov = np.cov(data, rowvar=False)
        eigenvalues, eigenvectors = np.linalg.eig(cov)
        idx = eigenvalues.argsort()[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]
        total = eigenvalues.sum()
        explained_var = 100 * eigenvalues / total
        if self.verbose:
            print(f"PC1: {explained_var[0]:.2f}%")
            print(f"PC2: {explained_var[1]:.2f}%")
        return eigenvalues, eigenvectors, explained_var

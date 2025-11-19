"""Test PCA Analysis"""
import sys
sys.path.insert(0, '../src')
import numpy as np
from pytermstructure.analysis import PCAAnalysis

def test_pca():
    np.random.seed(42)
    data = np.random.randn(50, 5)
    
    pca = PCAAnalysis()
    eigenvalues, eigenvectors, explained_var = pca.fit(data)
    
    assert eigenvalues is not None
    assert len(explained_var) == 5
    assert explained_var[0] > explained_var[1]
    print("✓ PCA test passed")

if __name__ == "__main__":
    test_pca()

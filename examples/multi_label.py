import numpy as np
from scipy import sparse

from sklearn.metrics import hamming_loss
from sklearn.datasets import fetch_mldata
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import mutual_info_score
from sklearn.utils.mst import minimum_spanning_tree

from pystruct.learners import OneSlackSSVM
from pystruct.models import MultiLabelModel


def chow_liu_tree(y):
    # compute mutual information using sklearn
    mi = np.zeros((14, 14))
    for i in xrange(14):
        for j in xrange(14):
            mi[i, j] = mutual_info_score(y[:, i], y[:, j])
    mst = minimum_spanning_tree(sparse.csr_matrix(-mi))
    return mst


def my_hamming(y_train, y_pred):
    return hamming_loss(y_train, np.vstack(y_pred))

yeast = fetch_mldata("yeast")

X = yeast.data
X = np.hstack([X, np.ones((X.shape[0], 1))])
y = yeast.target.toarray().astype(np.int).T


X_train, X_test = X[:1500], X[1500:]
y_train, y_test = y[:1500], y[1500:]


X_train.shape

#import itertools
#edges = np.vstack([x for x in itertools.combinations(range(14), 2)])
edges = np.zeros((0, 2), dtype=np.int)

model = MultiLabelModel(14, X.shape[1], edges=edges, inference_method='unary')

ssvm = OneSlackSSVM(model, inference_cache=0, verbose=0, n_jobs=1, C=.1,
                    show_loss_every=20, max_iter=10000, tol=0.01)

param_grid = {'C': 10. ** np.arange(-3, 1)}

grid = GridSearchCV(ssvm, loss_func=my_hamming, cv=5, n_jobs=-1, verbose=10,
                    param_grid=param_grid)
grid.fit(X_train, y_train)
#ssvm.fit(X_train, y_train)

from IPython.core.debugger import Tracer
Tracer()()

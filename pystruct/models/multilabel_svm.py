import numpy as np
from .crf import CRF


class MultiLabelModel(CRF):
    def __init__(self, n_labels, n_features, edges, inference_method='lp'):
        CRF.__init__(self, 2, n_features, inference_method)
        self.n_labels = n_labels
        self.edges = edges
        self.size_psi = n_features * n_labels + 4 * edges.shape[0]

    def get_edges(self, x):
        return self.edges

    def get_unary_potentials(self, x, w):
        unary_params = w[:self.n_labels * self.n_features].reshape(
            self.n_labels, self.n_features)
        unary_potentials = np.dot(x, unary_params.T)
        return np.vstack([-unary_potentials, unary_potentials]).T

    def get_pairwise_potentials(self, x, w):
        pairwise_params = w[self.n_labels * self.n_features:].reshape(
            self.edges.shape[0], self.n_states, self.n_states)
        return pairwise_params

    def psi(self, x, y):
        if isinstance(y, tuple):
            #from IPython.core.debugger import Tracer
            #Tracer()()
            y_cont, pairwise_marginals = y
            y_signs = 2 * y_cont[:, 1] - 1
            unary_marginals = np.repeat(x[np.newaxis, :], len(y_signs), axis=0)
            unary_marginals *= y_signs[:, np.newaxis]
        else:
            y_signs = 2 * y - 1
            unary_marginals = np.repeat(x[np.newaxis, :], len(y_signs), axis=0)
            unary_marginals *= y_signs[:, np.newaxis]
            pairwise_marginals = []
            for edge in self.edges:
                # indicator of one of four possible states of the edge
                pw = np.zeros((2, 2))
                pw[y[edge[0]], y[edge[1]]] = 1
                pairwise_marginals.append(pw)

        if len(pairwise_marginals):
            pairwise_marginals = np.vstack(pairwise_marginals)
            return np.hstack([unary_marginals.ravel(),
                              pairwise_marginals.ravel()])
        return unary_marginals.ravel()

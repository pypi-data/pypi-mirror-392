"""Matrix decomposition algorithms.

These include PCA, NMF, ICA, and more. Most of the algorithms of this module can be
regarded as dimensionality reduction techniques.
"""

# Authors: The scikit-learn developers
# SPDX-License-Identifier: BSD-3-Clause
# Relative imports only

from ._dict_learning import (
    dict_learning_online,
    dict_learning,
)

from ._factor_analysis import FactorAnalysis
from ._fastica import fastica
from ._incremental_pca import IncrementalPCA
from ._kernel_pca import KernelPCA
from ._pca import PCA
from ._sparse_pca import SparsePCA
from ._truncated_svd import TruncatedSVD
from ._nmf import NMF
from ._lda import LatentDirichletAllocation


__all__ = [
    "NMF",
    "PCA",
    "DictionaryLearning",
    "FactorAnalysis",
    "FastICA",
    "IncrementalPCA",
    "KernelPCA",
    "LatentDirichletAllocation",
    "MiniBatchDictionaryLearning",
    "MiniBatchNMF",
    "MiniBatchSparsePCA",
    "SparseCoder",
    "SparsePCA",
    "TruncatedSVD",
    "dict_learning",
    "dict_learning_online",
    "fastica",
    "non_negative_factorization",
    "randomized_svd",
    "sparse_encode",
]

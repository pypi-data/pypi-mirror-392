import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif, chi2

from pyensemblefs.ensemble.metabootstrapper import MetaBootstrapper


def test_metabootstrapper_selectkbest_scores_and_names():
    X, y = load_breast_cancer(return_X_y=True)
    p = X.shape[1]

    fs_methods = [
        SelectKBest(score_func=f_classif, k=10),
        SelectKBest(score_func=mutual_info_classif, k=10),
        SelectKBest(score_func=chi2, k=10),
    ]

    weights = {
        "SelectKBest_f_classif": 2.0,  # peso específico
        # "SelectKBest": 1.5  # opcional: comprobar compatibilidad por nombre de clase
    }

    boot = MetaBootstrapper(
        fs_methods=fs_methods,
        n_bootstraps=5,
        n_jobs=1,
        random_state=0,
        strategy="random",
        normalize_scores=True,
        method_weights=weights,
        verbose=False,
    )

    boot.fit(X, y)

    # 1) Matriz de máscaras debe existir y tener forma (B, p)
    assert boot.results_ is not None
    assert boot.results_.shape == (5, p)

    # 2) Debe existir score_mat_ y tener p columnas
    assert boot.score_mat_ is not None
    assert boot.score_mat_.shape[1] == p

    # 3) Los métodos usados deben incluir sufijos de score_func
    methods = set(boot.methods_used_)
    assert any("SelectKBest_f_classif" in m for m in methods)
    assert any("SelectKBest_mutual_info_classif" in m for m in methods)
    assert any("SelectKBest_chi2" in m for m in methods)

    # 4) Scores normalizados en [0, 1]
    scores_flat = boot.score_mat_.ravel()
    assert np.all(scores_flat >= 0.0)
    assert np.all(scores_flat <= 1.0)

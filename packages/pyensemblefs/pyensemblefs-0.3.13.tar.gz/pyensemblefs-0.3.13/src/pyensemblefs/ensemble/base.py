import os
import numpy as np
import pandas as pd
from joblib import Parallel, delayed

import matplotlib
import random

from itertools import chain
import logging
import coloredlogs
from typing import Tuple, Dict, Any

from pyensemblefs.fsmethods.fs_factory import get_fs_method
from pyensemblefs.fsmethods.fs_factory import FS_METHODS
from pyensemblefs import fsmethods.relief

matplotlib.logging.getLogger('matplotlib.font_manager').disabled = True
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


def get_bootstrap_sample(df_data: pd.DataFrame,
                         labels: np.array,
                         random_state: int
                         ) -> Dict:
    """
    This function takes as input the data and labels and returns
    a bootstrap sample of the data, as well as its out-of-bag (OOB) data

    INPUTS:
    - data is a 2-dimensional pd.DataFrame or numpy.ndarray where rows are examples and columns are features
    - labels is a 1-dimensional numpy.ndarray giving the label of each example in data

    OUPUT:
    - a dictionnary where:
          - key 'bootData' gives a 2-dimensional numpy.ndarray which is a bootstrap sample of data
          - key 'bootLabels' is a 1-dimansional numpy.ndarray giving the label of each example in bootData
          - key 'OOBData' gives a 2-dimensional numpy.ndarray the OOB examples
          - key 'OOBLabels' is a 1-dimansional numpy.ndarray giving the label of each example in OOBData
    """

    df_data_copy = df_data.copy()
    df_data = df_data_copy.to_numpy()
    n_samples, n_features = df_data.shape
    if n_samples != len(labels):
        raise ValueError('The data and labels should have a same number of rows.')

    np.random.seed(random_state)

    ind = np.random.choice(range(n_samples), size=n_samples, replace=True)
    oo_bind = np.setdiff1d(range(n_samples), ind, assume_unique=True)
    boot_data = df_data[ind, ]
    boot_labels = labels[ind]

    oob_data = df_data[oo_bind, ]
    oob_labels = labels[oo_bind]

    dict_boot_data = {
        'id_boot': random_state,
        'boot_data': boot_data,
        'boot_labels': boot_labels,
        'oob_data': oob_data,
        'oob_labels': oob_labels
    }

    return dict_boot_data



def set_seed_reproducibility(seed):
    """
    Generating the seed to keep our randomness constant.

    Parameters
    ----------
    seed : int
        Seed to be used throughout the process

    Returns
    -------
    Seed

    """
    np.random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    random.seed(seed)


def compute_zmatrix_bootstrap(df_features: pd.DataFrame,
                              y_label: np.array,
                              fs_method_name: str,
                              list_feature_names: list,
                              list_vars_categorical: list,
                              list_vars_numerical: list,
                              n_boots: int = 100,
                              verbose: bool = False,
                              n_jobs: int = 1
                              ) -> Tuple[np.array, np.array]:

    logger.info('Train homogeneous ensemble fs with data {}'.format(df_features.shape))

    n_samples, n_features = df_features.shape
    k_values = range(n_features)
    y_label = y_label.reshape(n_samples)

    Z_selected = np.zeros((len(k_values), n_boots, n_features), dtype=np.int16)
    Z_scores = np.zeros((len(k_values), n_boots, n_features), dtype=np.float16)

    list_n_boots = list(range(n_boots))
    list_dict_boot_data = [get_bootstrap_sample(df_features, y_label, id_boot) for id_boot in list_n_boots]

    list_dict_fs_result = Parallel(n_jobs=n_jobs)(
        delayed(train_fs_method_by_bootstrap)(dict_boot_data,
                                              fs_method_name,
                                              list_feature_names,
                                              list_vars_categorical,
                                              list_vars_numerical,
                                              verbose
                                              ) for dict_boot_data in list_dict_boot_data
    )

    for id_bootstrap in list_n_boots:

        dict_fs_result = list(filter(lambda dict_fs: dict_fs['id_boot'] == id_bootstrap, list_dict_fs_result))[0]

        for k_features in k_values:
            df_k_features = dict_fs_result['k_features_all'].iloc[:, :k_features + 1]
            df_k_scores = dict_fs_result['k_scores_all'].iloc[:k_features + 1, :]
            v_col_names_k_features = df_k_features.columns.values
            top_k_scores = df_k_scores['score'].values
            top_k = dict_fs_result['boot_data'].columns.get_indexer(v_col_names_k_features)
            Z_selected[k_features, id_bootstrap, top_k] = 1
            Z_scores[k_features, id_bootstrap, top_k] = top_k_scores
            logger.info('boot: {}, k_values: {}, scores: {}'.format(id_bootstrap, k_features + 1, list(top_k_scores)))

    return Z_selected, Z_scores

def train_fs_method_by_bootstrap(dict_boot_data: dict,
                                 fs_method_name: str,
                                 v_feature_names: np.array,
                                 list_vars_categorical: list,
                                 list_vars_numerical: list,
                                 verbose: bool = False
                                 ) -> Dict[str, Any]:

    logger.info('Train fs: {}, with boot: {}'.format(fs_method_name, dict_boot_data['id_boot'], dict_boot_data['boot_data']))

    if isinstance(dict_boot_data['boot_data'], np.ndarray):
        dict_boot_data['boot_data'] = pd.DataFrame(np.squeeze(dict_boot_data['boot_data']), columns=v_feature_names)

    n_samples, n_features = dict_boot_data['boot_data'].shape
    fs_method = get_fs_method(fs_method_name)

    if fs_method is None:
        raise ValueError("fs_method is None. This means it was not found in FS_METHODS. "
                         f"Check the name used for registration and retrieval.")

    fs_method.fit(dict_boot_data['boot_data'],
                  dict_boot_data['boot_labels'],
                  n_features,
                  list_vars_categorical,
                  list_vars_numerical,
                  verbose
                  )
    df_k_features_all, df_k_scores_all = fs_method.extract_features()

    dict_fs_result = {
        'id_boot': dict_boot_data['id_boot'],
        'boot_data': dict_boot_data['boot_data'],
        'k_features_all': df_k_features_all,
        'k_scores_all': df_k_scores_all
    }

    return dict_fs_result


def run_ensemble_agg(df_features: pd.DataFrame,
                     Z_selected: np.array,
                     Z_scores: np.array,
                     agg_func: str = 'all'
                     ):

    n_samples, n_features = df_features.shape
    v_col_names = df_features.columns.values

    agg_func = get_agg_func(agg_func)

    list_v_agg_selected = []
    list_v_agg_scores = []
    for k_features in range(n_features):
        v_agg_k_features_selected = np.sum(Z_selected[k_features, :, :], axis=0)
        v_agg_k_features_scores = agg_func(Z_scores[k_features, :, :], axis=0)
        list_v_agg_selected.append(v_agg_k_features_selected)
        list_v_agg_scores.append(v_agg_k_features_scores)

    v_ensemble_voting = np.sum(np.asarray(list_v_agg_selected), axis=0)
    v_ensemble_agg = agg_func(np.asarray(list_v_agg_scores), axis=0)

    df_ensemble_voting = pd.DataFrame({'var_name': v_col_names, 'score': v_ensemble_voting})
    df_ensemble_simple = pd.DataFrame({'var_name': v_col_names, 'score': v_ensemble_agg})

    df_ensemble_voting_sorted = df_ensemble_voting.sort_values(by=['score'], ascending=False)
    df_ensemble_agg_sorted = df_ensemble_simple.sort_values(by=['score'], ascending=False)

    return df_ensemble_voting_sorted, df_ensemble_agg_sorted


def get_bbdd_name(bbdd_name):
    return bbdd_name


def get_normalized_data_features(x_features, v_feature_names, scaler_num, scaler_cat):
    df_features = pd.DataFrame(x_features, columns=v_feature_names)
    df_features[list_vars_numerical] = scaler_num.fit_transform(df_features[list_vars_numerical].values)
    df_features[list_vars_categorical] = scaler_cat.fit_transform(df_features[list_vars_categorical].values)

    return df_features


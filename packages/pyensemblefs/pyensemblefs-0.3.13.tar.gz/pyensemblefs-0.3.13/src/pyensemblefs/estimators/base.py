import pandas as pd
import numpy as np


def train_fs_clf_with_different_k_features(df_features: pd.DataFrame,
                                           y_label: np.array,
                                           fs_method_name: str,
                                           bbdd_name: str,
                                           estimator_name: str = 'dt',
                                           as_frame: bool = False,
                                           scoring_estimator: str = 'roc_auc',
                                           df_ensemble_ranked_features: pd.DataFrame = None,
                                           type_ensemble: str = 'voting',
                                           n_jobs: int = 1
                                           ):
    """
    Train our datasets with different features

    Parameters
    ----------

    df_features : Pandas dataframe
        We define the features' matrix we are going to train the classifier with
    y_label : Label vector
        We define the label vector to train the classifier
    fs_method_name : str
        We define the feature selection method we are going to use
    bbdd_name: str
        Name of bbdd
    estimator_name : str
        We define the classifier we want to use
    as_frame: bool
        Return dataframe
    scoring_estimator: str
        scoring for grid_search
    df_ensemble_ranked_features: pd.DataFrame
        Dataframe with ensemble results
    Returns
    -------
    df_metrics : Pandas dataframe
        Returns a dataframe with the metrics for each k feature of the dataset.
    df_feature_ranked_scores : Pandas dataframe
        Returns a matrix containing the scores (relevances) for each feature.
    """

    df_features_copy = df_features.copy()
    n_features = df_features.shape[1]

    if df_ensemble_ranked_features is None:
        fs_method = get_fs_method(fs_method_name)
        fs_method.fit(df_features, y_label, n_features, list_vars_categorical, list_vars_numerical)
        df_filtered, df_feature_ranked_scores = fs_method.extract_features()
        v_ranked_feature_names = df_feature_ranked_scores['var_name'].values
    else:
        v_ranked_feature_names = df_ensemble_ranked_features['var_name'].values
        df_feature_ranked_scores = df_ensemble_ranked_features

    list_k_range_features = list(range(1, n_features + 1))

    list_total_metrics = Parallel(n_jobs=n_jobs)(
        delayed(train_with_several_partitions_by_clf)(
            df_features_copy.loc[:, v_ranked_feature_names[:k_features]].values,
            y_label,
            estimator_name,
            fs_method_name,
            bbdd_name,
            k_features=k_features,
            as_frame=as_frame,
            score_estimator=scoring_estimator,
            type_ensemble=type_ensemble,
            verbose=True
            ) for k_features in list_k_range_features
    )

    list_total_metrics_flat = list(chain.from_iterable(list_total_metrics))

    if as_frame:
        df_metrics = pd.DataFrame(list_total_metrics_flat)
        return df_metrics, df_feature_ranked_scores
    else:
        return list_total_metrics_flat, df_feature_ranked_scores


def select_optimal_features_ensemblefs(X,
                                       y,
                                       df_voting_sorted,
                                       v_img_name,
                                       estimator_name,
                                       scoring_estimator,
                                       seed_value
                                       ):
    list_total_metrics = []

    for per_features in range(10, 110, 10):
        n_selected_features = round(df_voting_sorted.shape[0] * (per_features / 100))
        v_selected_features = df_voting_sorted.iloc[:n_selected_features, :]['var_name']
        df_selected_features = X.loc[:, v_selected_features]

        list_df_metrics = train_clf_with_selected_features(df_selected_features,
                                                           y,
                                                           bbdd_name='',
                                                           estimator_name=estimator_name,
                                                           as_frame=False,
                                                           scoring_estimator=scoring_estimator,
                                                           )

        list_total_metrics.extend(list_df_metrics)
    df_metrics = pd.DataFrame(list_total_metrics)
    print(df_metrics)
    df_scoring_clf = df_metrics[(df_metrics['metric'] == scoring_estimator)]
    best_k_features = df_scoring_clf.loc[df_scoring_clf['mean'].idxmax()]['k_features']
    v_best_features = df_voting_sorted.iloc[:best_k_features, :]['var_name']
    df_best_features = X.loc[:, v_best_features]
    df_best_features['img_name'] = v_img_name
    path_stats = Path.joinpath(consts.PATH_PROJECT_DIR, 'data', 'fs', 'ph2', f'statistics_FS_{seed_value}_PH2.csv')
    df_best_features.to_csv(str(path_stats), index=False)

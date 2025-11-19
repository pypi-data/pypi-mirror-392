import numpy as np
from sklearn.metrics import accuracy_score, recall_score, roc_auc_score, precision_score
from sklearn.metrics import confusion_matrix, classification_report, f1_score
from typing import Dict
from pyensemblefs.utils.plotter import plot_confusion_matrix


def get_metric_classification(scoring_metric, n_classes, average='macro'):

    if n_classes == 2:
        return scoring_metric
    else:
        if scoring_metric == 'roc_auc':
            return '{}_{}'.format(scoring_metric, 'ovo')
        elif scoring_metric == 'f1':
            return '{}_{}'.format(scoring_metric, average)


def compute_classification_prestations(y_true: np.array,
                                       y_pred: np.array,
                                       y_pred_prob: np.array,
                                       class_names: np.array,
                                       verbose=False,
                                       show_confusion_matrix=False
                                       ) -> (float, float, float, float):
    n_classes = len(set(y_true))

    print('y-true: ', np.unique(y_true))
    print('y-pred: ', np.unique(y_pred))

    if verbose:
        print(classification_report(y_true, y_pred))

    if show_confusion_matrix:
        cm = confusion_matrix(y_true, y_pred)
        plot_confusion_matrix(cm, class_names=class_names)

    if n_classes == 2:
        return {'accuracy': accuracy_score(y_true, y_pred),
                'precision': precision_score(y_true, y_pred),
                'specificity': specificity_score(y_true, y_pred),
                'recall': recall_score(y_true, y_pred),
                'roc_auc': roc_auc_score(y_true, y_pred),
                'f1': f1_score(y_true, y_pred)
        }
    else:
        return compute_multiclass_metrics(y_true, y_pred, y_pred_prob, average)


def compute_multiclass_metrics(y_true, y_pred, y_pred_proba, avg='micro') -> Dict[str, float]:

    dict_metrics_report = {
        'precision': precision_score(y_true, y_pred, average=avg),
        'specificity': specificity_score(y_true, y_pred, average=avg),
        'recall': recall_score(y_true, y_pred, average=avg),
        'roc_auc': roc_auc_score(y_true, y_pred_proba, multi_class='ovr', average=avg),
        'f1': f1_score(y_true, y_pred, average=avg)
    }

    return dict_metrics_report


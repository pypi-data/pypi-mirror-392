# -*- coding: utf-8 -*-
from __future__ import annotations
from .pima import load_pima_dataset
from .breast_cancer import load_breast_cancer_dataset
from .heart import load_heart_dataset
from .diabetes_sklearn import load_sklearn_diabetes_dataset

__all__ = [
    "load_pima_dataset",
    "load_breast_cancer_dataset",
    "load_heart_dataset",
    "load_sklearn_diabetes_dataset",
]
from pathlib import Path


DATASET_REGISTRY = {
    "wine": "https://archive.ics.uci.edu/ml/machine-learning-databases/wine/wine.data",
    "iris": "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data",
    "breast_cancer": "https://archive.ics.uci.edu/ml/machine-learning-databases/breast-cancer-wisconsin/wdbc.data",
    "glass": "https://archive.ics.uci.edu/ml/machine-learning-databases/glass/glass.data",
    "ionosphere": "https://archive.ics.uci.edu/ml/machine-learning-databases/ionosphere/ionosphere.data",
    "seeds": "https://archive.ics.uci.edu/ml/machine-learning-databases/00236/seeds_dataset.txt",
}

PATH_PROJECT_RESULTS = Path("results")
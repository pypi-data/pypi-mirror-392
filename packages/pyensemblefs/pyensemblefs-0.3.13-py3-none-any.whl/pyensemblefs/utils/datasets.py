from pathlib import Path
import numpy as np
import pandas as pd
import requests
import zipfile
from pyensemblefs.utils import consts as cons


def download_file(url, target_path, chunk_size=1024, verbose=False):
    target_path = Path(target_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if target_path.exists():
        if verbose:
            print(f"File already exists: {target_path}")
        return target_path
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(target_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=chunk_size):
            f.write(chunk)
    if verbose:
        print(f"Downloaded: {target_path}")
    return target_path


def load_external_dataset(name, path="data", force_download=False, verbose=True):
    """
    Download and load a dataset by name from the registry
    """
    name = name.lower()
    if name not in cons.DATASET_REGISTRY:
        raise ValueError(f"Dataset '{name}' not available. Available: {list(cons.DATASET_REGISTRY.keys())}")

    url = cons.DATASET_REGISTRY[name]
    full_path = Path(path)/name
    full_path.mkdir(parents=True, exist_ok=True)

    file_name = url.split("/")[-1]
    file_path = full_path/file_name

    if force_download or not file_path.exists():
        download_file(url, file_path, verbose=verbose)

    if file_path.suffix in [".data", ".csv", ".txt"]:
        df = pd.read_csv(file_path, header=None)
        # TODO Fix last column = target
        X = df.iloc[:, :-1].values
        y = df.iloc[:, -1].values
    else:
        raise ValueError(f"Unsupported file type: {file_path.suffix}")

    if verbose:
        print(f"Loaded dataset {name}: X={X.shape}, y={y.shape}")

    return X, y

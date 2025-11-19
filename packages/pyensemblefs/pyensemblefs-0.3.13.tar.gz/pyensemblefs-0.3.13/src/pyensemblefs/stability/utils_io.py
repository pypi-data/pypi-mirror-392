# -*- coding: utf-8 -*-
from __future__ import annotations
import json
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
from scipy import sparse as sp


def load_features(path: Path) -> List[list]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("features JSON must be a list of lists")
    for i, s in enumerate(data):
        if not isinstance(s, list):
            raise ValueError(f"features[{i}] must be a list")
    return data


def load_sim_matrix(path: Path) -> Tuple[object, Optional[List]]:
    labels = None
    suffix = path.suffix.lower()
    if suffix == ".npz":
        try:
            M = sp.load_npz(path)
        except Exception:
            obj = np.load(path, allow_pickle=True)
            if hasattr(obj, "item"):
                obj = obj.item()
            if isinstance(obj, dict) and "data" in obj:
                M = sp.coo_matrix((obj["data"], (obj["row"], obj["col"])), shape=tuple(obj["shape"]))
            else:
                raise
    elif suffix in {".npy"}:
        M = np.load(path)
    elif suffix in {".csv", ".tsv"}:
        delimiter = "," if suffix == ".csv" else "\t"
        M = np.loadtxt(path, delimiter=delimiter)
    else:
        raise ValueError("Unsupported sim-mat format. Use .npz (sparse), .npy, .csv or .tsv")

    lbl_path = path.with_suffix(path.suffix + ".labels.json")
    if lbl_path.exists():
        with open(lbl_path, "r", encoding="utf-8") as f:
            labels = json.load(f)
    return M, labels
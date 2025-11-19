from __future__ import annotations
import argparse
import glob
import json
import logging
import os
from typing import List, Dict, Any


def is_ranking_item(obj: Any) -> bool:
    return isinstance(obj, dict) and "feature" in obj


def load_ranking_as_list(path: str) -> List[str]:
    data = json.load(open(path, "r", encoding="utf-8"))
    if not isinstance(data, list) or len(data) == 0:
        raise ValueError(f"{path}: expected a non-empty list for ranking JSON.")
    if is_ranking_item(data[0]):
        data = sorted(
            data,
            key=lambda d: d.get("score", float("inf")),
            reverse=True,
        )
        return [str(d["feature"]) for d in data]
    if all(isinstance(x, (str, int)) for x in data):
        return [str(x) for x in data]
    raise ValueError(f"{path}: unrecognized ranking structure.")


def load_subset_features(path: str) -> List[str]:
    data = json.load(open(path, "r", encoding="utf-8"))
    if not isinstance(data, dict) or "selected_features" not in data:
        raise ValueError(f"{path}: expected a dict with key 'selected_features'.")
    feats = data["selected_features"]
    if not isinstance(feats, list) or not all(isinstance(x, (str, int)) for x in feats):
        raise ValueError(f"{path}: 'selected_features' must be a list of strings/ints.")
    return [str(x) for x in feats]


def write_json(path: str, obj: Any) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def main():
    ap = argparse.ArgumentParser(
        description="Aggregate ranking_* and subset_* JSON files into feature set lists for main_stab.py."
    )
    ap.add_argument(
        "--base-dir",
        type=str,
        default="data/test_ranking_subset",
        help="Directory containing ranking_*.json and subset_*.json files.",
    )
    ap.add_argument(
        "--topk",
        type=int,
        default=5,
        help="Top-k to take from each ranking file when converting to subsets.",
    )
    ap.add_argument(
        "--rankings-pattern",
        type=str,
        default="ranking_*.json",
        help="Glob pattern (relative to base-dir) for ranking files.",
    )
    ap.add_argument(
        "--subsets-pattern",
        type=str,
        default="subset_*.json",
        help="Glob pattern (relative to base-dir) for subset files.",
    )
    ap.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity.",
    )
    args = ap.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="[%(levelname)s] %(message)s",
    )

    base = args.base_dir
    ranking_paths = sorted(glob.glob(os.path.join(base, args.rankings_pattern)))
    subset_paths = sorted(glob.glob(os.path.join(base, args.subsets_pattern)))

    logging.info("Base dir: %s", base)
    logging.info("Found %d ranking file(s) and %d subset file(s).", len(ranking_paths), len(subset_paths))

    ranking_sets: List[List[str]] = []
    for rp in ranking_paths:
        try:
            ranking = load_ranking_as_list(rp)
            subset = ranking[: args.topk]
            ranking_sets.append(subset)
            logging.debug("Ranking %s -> Top-%d subset: %s", os.path.basename(rp), args.topk, subset)
        except Exception as e:
            logging.error("Failed to parse ranking file %s: %s", rp, e)
            raise

    subset_sets: List[List[str]] = []
    for sp in subset_paths:
        try:
            feats = load_subset_features(sp)
            subset_sets.append(feats)
            logging.debug("Subset %s -> %s", os.path.basename(sp), feats)
        except Exception as e:
            logging.error("Failed to parse subset file %s: %s", sp, e)
            raise

    out_rank = os.path.join(base, "features_from_rankings_topk.json")
    out_subs = os.path.join(base, "features_from_subsets.json")

    write_json(out_rank, ranking_sets)
    write_json(out_subs, subset_sets)

    union_rank = sorted({f for s in ranking_sets for f in s})
    union_subs = sorted({f for s in subset_sets for f in s})

    logging.info("Wrote %s with %d set(s). Union size=%d.", out_rank, len(ranking_sets), len(union_rank))
    logging.info("Wrote %s with %d set(s). Union size=%d.", out_subs, len(subset_sets), len(union_subs))
    logging.info("Tip: pass --p <TOTAL_FEATURES_IN_DATASET> to main_stab.py for measures that require it.")


if __name__ == "__main__":
    main()
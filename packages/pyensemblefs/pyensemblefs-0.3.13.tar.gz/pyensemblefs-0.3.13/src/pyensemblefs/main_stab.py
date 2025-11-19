# -*- coding: utf-8 -*-
"""
CLI to compute stability of feature selection, faithfully ported from the R code.
"""
import argparse
import json
import logging
import math
from pathlib import Path
from typing import Any, Dict, List, Union

from pyensemblefs.stability.stability import stability
from pyensemblefs.stability.utils_io import load_sim_matrix, load_features


RANKING_MEASURES = {"yu", "zucknick", "sechidis"}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Compute stability measures (R→Python port)")
    p.add_argument(
        "--features",
        type=str,
        required=True,
        help=(
            "Path to a JSON file. "
            "For subset measures: a list of feature sets (each set a list of ints/strs). "
            "For ranking measures (yu, zucknick, sechidis): a ranking or list of rankings "
            "([{'feature': name, 'score': val}, ...] or ['f1','f2',...])."
        ),
    )
    p.add_argument(
        "--measure",
        type=str,
        required=True,
        help=(
            "Measure key (lowercase, exactly as in R):\n"
            "  adjusted intersections: intersection.mbm | intersection.greedy | intersection.count | intersection.mean | intersection.common\n"
            "  adjusted others: yu | zucknick | sechidis\n"
            "  unadjusted: davis | dice | hamming | jaccard | kappa.coefficient | lustgarten | nogueira | novovicova | ochiai | phi.coefficient | somol | wald\n"
        ),
    )
    p.add_argument("--correction-for-chance", type=str, default="none", choices=["none", "estimate", "exact", "unadjusted"], help="Chance correction mode. For 'intersection.common' R forces 'unadjusted'.",)
    p.add_argument("--N", type=int, default=None, help="Number of random samples when correction-for-chance=estimate.",)
    p.add_argument("--p", type=int, default=None, help="Total number of features (required for some measures/corrections).",)
    p.add_argument("--penalty", type=float, default=None, help="Penalty parameter for 'davis'.",)
    p.add_argument("--sim-mat", type=str, default=None, help="Similarity matrix file. CSV/TSV (dense) or .npz (scipy sparse). Required for adjusted measures.",)
    p.add_argument("--threshold", type=float, default=None, help="Similarity threshold in [0,1] to zero-out entries for adjusted measures.",)
    p.add_argument("--impute-na", type=float, default=None, help="Impute value for NA/NaN scores. If omitted, NaNs propagate to final mean.",)
    p.add_argument("--log-level", type=str, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="Logging verbosity.",)
    p.add_argument("--output-json", type=str, default=None, help="Optional path to write a JSON result with {'score': <float>}",)
    p.add_argument("--topk", type=int, default=None, help="Top-k features to take from each ranking (only used for ranking measures: yu, zucknick, sechidis).",)
    p.add_argument("--topk-ratio", type=float, default=None, help="Alternative to --topk: ceil(ratio * p) (only for ranking measures).",)
    return p



def _load_payload(path: Union[str, Path]) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _is_ranking_item(x: Any) -> bool:
    return isinstance(x, dict) and "feature" in x


def _ranking_to_list(r: Union[List[Any], List[Dict[str, Any]]]) -> List[str]:
    if isinstance(r, list) and r and _is_ranking_item(r[0]):
        r_sorted = sorted(r, key=lambda d: d.get("score", float("inf")), reverse=True)
        return [str(d["feature"]) for d in r_sorted]
    if isinstance(r, list) and all(isinstance(z, (str, int)) for z in r):
        return [str(z) for z in r]
    raise ValueError("Ranking structure not recognized. Use list of {'feature', 'score?'} or list of names.")


def _ensure_list_of_lists(obj: Any) -> List[List[str]]:
    if isinstance(obj, list) and obj and all(isinstance(s, list) for s in obj):
        return [[str(z) for z in s] for s in obj]
    if isinstance(obj, list) and (not obj or all(isinstance(z, (str, int)) for z in obj)):
        return [[str(z) for z in obj]]
    raise ValueError("Expected a list of lists for subset input.")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level),
                        format="[%(levelname)s] %(message)s")

    measure_key = args.measure.strip().lower()

    sim_mat = None
    sim_labels = None
    if args.sim_mat is not None:
        sim_mat, sim_labels = load_sim_matrix(Path(args.sim_mat))
        logging.info("Loaded similarity matrix with shape %s.", tuple(sim_mat.shape))

    threshold = args.threshold
    if threshold is None and measure_key in {
        "zucknick", "yu", "intersection.mbm", "intersection.greedy",
        "intersection.count", "intersection.mean"
    }:
        threshold = 0.9
    if threshold is None and measure_key == "sechidis":
        threshold = 0.9

    if measure_key in RANKING_MEASURES:
        payload = _load_payload(args.features)

        if isinstance(payload, list) and payload and isinstance(payload[0], list):
            rankings = [_ranking_to_list(r) for r in payload]
        elif isinstance(payload, list):
            rankings = [_ranking_to_list(payload)]
        else:
            raise ValueError(
                "For ranking measures (yu, zucknick, sechidis), "
                "--features must be a ranking or a list of rankings."
            )

        p_inferred = len(rankings[0]) if rankings else None
        if args.p is None and p_inferred is not None:
            args.p = p_inferred
            logging.info("Inferred p=%d from ranking length.", args.p)

        if args.topk is not None:
            k = int(args.topk)
        elif args.topk_ratio is not None and args.p is not None:
            k = int(math.ceil(args.topk_ratio * args.p))
        else:
            k = min(5, args.p) if args.p is not None else 5  

        if args.p is not None and not (1 <= k <= args.p):
            raise ValueError(f"Invalid --topk={k} for p={args.p}. Use 1..p.")

        features = [r[:k] for r in rankings]
        logging.info(
            "Measure '%s' expects RANKING. Converted %d ranking(s) to Top-%d subsets.",
            args.measure, len(features), k
        )

    else:
        features = load_features(Path(args.features))
        logging.info("Measure '%s' expects SUBSETS. Loaded %d set(s).", args.measure, len(features))

    score = stability(
        features=features,
        measure=measure_key,
        correction_for_chance=args.correction_for_chance,
        N=args.N,
        impute_na=args.impute_na,
        p=args.p,
        sim_mat=sim_mat,
        sim_labels=sim_labels,
        threshold=threshold,
        penalty=args.penalty,
    )

    logging.info(
        "Stability score: %s",
        "nan" if (score is None or (isinstance(score, float) and math.isnan(score))) else f"{score:.6f}"
    )

    if args.output_json:
        out: Dict[str, Any] = {"score": None if score is None else float(score)}
        Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output_json, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)
        logging.info("Saved result to %s", args.output_json)


if __name__ == "__main__":
    main()

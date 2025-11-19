import argparse
import logging
import os
import sys
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def setup_logger(verbosity: int) -> None:
    level = logging.INFO if verbosity == 0 else logging.DEBUG
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build cosine similarity matrix between columns (features).")
    parser.add_argument("--data", required=True, help="Path to input CSV dataset.")
    parser.add_argument(
        "--out",
        required=False,
        default="similarity_matrix_columns.csv",
        help="Output CSV file for the column-wise similarity matrix."
    )
    parser.add_argument(
        "--standardize",
        action="store_true",
        help="If set, standardize numeric features (z-score per column)."
    )
    parser.add_argument(
        "--dropna",
        action="store_true",
        help="If set, drop rows with any NA in numeric features before computing similarity."
    )
    parser.add_argument("--sep", default=",", help="CSV delimiter (default: ',').")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logs.")
    return parser.parse_args()

def zscore(df: pd.DataFrame) -> pd.DataFrame:
    return (df - df.mean()) / df.std(ddof=0)

def main() -> None:
    args = parse_args()
    setup_logger(0 if not args.verbose else 1)

    if not os.path.isfile(args.data):
        logging.info(f"Input file not found: {args.data}")
        sys.exit(1)

    logging.info(f"Loading dataset from: {args.data}")
    df = pd.read_csv(args.data, sep=args.sep)

    num_df = df.select_dtypes(include=[np.number]).copy()
    logging.info(f"Total columns: {df.shape[1]} | Numeric columns: {num_df.shape[1]}")

    if num_df.shape[1] == 0:
        logging.info("No numeric columns found. Aborting.")
        sys.exit(1)

    if args.dropna:
        before = num_df.shape[0]
        num_df = num_df.dropna(axis=0)
        logging.info(f"Dropped rows with NA: {before - num_df.shape[0]} (remaining rows: {num_df.shape[0]})")
    else:
        num_df = num_df.fillna(num_df.mean(numeric_only=True))
        logging.info("Filled NA values with column means.")

    if args.standardize:
        logging.info("Applying z-score standardization (per column).")
        num_df = zscore(num_df)
        num_df = num_df.replace([np.inf, -np.inf], np.nan).fillna(0.0)

    logging.info("Computing cosine similarity between columns (features).")
    sim = cosine_similarity(num_df.values.T)

    feature_names = num_df.columns.astype(str)
    sim_df = pd.DataFrame(sim, index=feature_names, columns=feature_names)

    logging.info(f"Saving similarity matrix to: {args.out}")
    sim_df.to_csv(args.out, index=True)

    logging.info("Done.")

if __name__ == "__main__":
    main()
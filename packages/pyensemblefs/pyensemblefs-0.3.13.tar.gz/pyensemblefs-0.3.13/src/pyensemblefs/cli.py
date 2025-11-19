# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os
import logging

from pyensemblefs.ensemble.bootstrapper import Bootstrapper
from pyensemblefs.ensemble.metabootstrapper import MetaBootstrapper
from pyensemblefs.ensemble.featureselector import FeatureSelector
from pyensemblefs.fsmethods.factory import get_fs_method, FS_METHODS

LOG = logging.getLogger("pyensemblefs")

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pyefs",
        description="Ensemble Feature Selection & Stability"
    )
    p.add_argument("--mode", choices=["bootstrap","metabootstrap","pipeline"], default="bootstrap",
                   help="Which high-level flow to run.")
    p.add_argument("--n-bootstrap", type=int, default=50, help="Bootstrap iterations.")
    p.add_argument("--method", choices=FS_METHODS, default="anova", help="Base FS method.")
    p.add_argument("--save-dir", type=str, default=None, help="Directory to save figures (no GUI).")
    p.add_argument("--no-show", action="store_true", help="Do not call plt.show().")
    p.add_argument("--verbose", action="store_true", help="Verbose logging.")
    return p

def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    os.environ.setdefault("MPLBACKEND", "Agg")
    no_show = True if os.environ.get("MPLBACKEND") == "Agg" else False
    if args.no_show:
        no_show = True

    LOG.info("Selected FS method: %s", args.method)
    _ = get_fs_method(args.method)

    if args.mode == "bootstrap":
        pass
    elif args.mode == "metabootstrap":
        pass
    elif args.mode == "pipeline":
        pass

    if args.save_dir:
        os.makedirs(args.save_dir, exist_ok=True)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
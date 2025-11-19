MEASURE_DEFAULT_CORR = {
    # unadjusted
    "davis": "none",
    "dice": "none",
    "hamming": "none",
    "jaccard": "none",
    "novovicova": "none",
    "ochiai": "none",
    "kappa.coefficient": "none",
    "lustgarten": "none",
    "nogueira": "none",
    "phi.coefficient": "none",
    "somol": "none",
    "wald": "none",
    "sechidis": "none",
    # adjusted — use Monte Carlo like stabm when N is provided
    "intersection.count": "estimate",
    "intersection.greedy": "estimate",
    "intersection.mbm": "estimate",
    "intersection.mean": "estimate",
    "yu": "estimate",
    "zucknick": "estimate",
}

# Monte Carlo samples when using "estimate"
N_ESTIMATE_DEFAULT = 500

# Threshold default for adjusted measures (avoid degeneracy when sim is dense-positive)
ADJUSTED_THRESHOLD_DEFAULT = 0.30

# Similarity matrix default when not provided: exponential decay 0.9^|i-j|
SIM_EXP_BASE = 0.9

# Compatibility guard: define 0.0 instead of NaN in exact degeneracy (score == E == max)
RETURN_ZERO_ON_DEGENERACY = True

from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_breast_cancer
from sklearn.feature_selection import SelectKBest, mutual_info_classif
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

from pyensemblefs.ensemble.featureselector import EnsembleFeatureSelector
from pyensemblefs.ensemble.bootstrapper import Bootstrapper
from pyensemblefs.aggregators.rank import MeanRankAggregator

from pyensemblefs.estimators.evaluator import compute_classification_prestations


# Load data
X, y = load_breast_cancer(return_X_y=True)

# Train/test split (fix undefined variables in the original script)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

# Base univariate FS (scores per feature)
fs = SelectKBest(score_func=mutual_info_classif, k=20)

# Ensemble feature selector with Bootstrapper and MeanRank aggregation
efs_pipeline = EnsembleFeatureSelector(
    bootstrapper=Bootstrapper(fs, n_bootstraps=50, n_jobs=4, random_state=42),
    aggregator=MeanRankAggregator(),
    k=10
)

pipeline = Pipeline([
    ('ensemble_feature_selection', efs_pipeline),
    ('scaler', StandardScaler()),
    ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
])

# Fit & evaluate
pipeline.fit(X_train, y_train)
y_test_pred = pipeline.predict(X_test)

compute_classification_prestations(y_test, y_test_pred)
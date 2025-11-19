"""
TabPFN Client Example Usage
--------------------------
Toy script to check that the TabPFN client is working.
Use the breast cancer dataset for classification and the diabetes dataset for regression,
and try various prediction types.
"""

import logging
from unittest.mock import patch

from sklearn.datasets import load_breast_cancer, load_diabetes
from sklearn.model_selection import train_test_split

# from tabpfn_client import UserDataClient
from tabpfn_client.estimator import TabPFNClassifier, TabPFNRegressor
from tabpfn_client.constants import ModelVersion

logging.basicConfig(level=logging.INFO)

FULL_BREAST_CANCER_DESCRIPTION = """**Breast Cancer Wisconsin (Original) Data Set.** Features are computed from a digitized image of a fine needle aspirate (FNA) of a breast mass. They describe characteristics of the cell nuclei present in the image. The target feature records the prognosis (malignant or benign)."""


if __name__ == "__main__":
    # Patch webbrowser.open to prevent browser login
    with patch("webbrowser.open", return_value=False):
        X, y = load_breast_cancer(return_X_y=True)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.33, random_state=42
        )

        tabpfn = TabPFNClassifier.create_default_for_version(
            ModelVersion.V2_5, n_estimators=3, thinking=True, thinking_params={'datascientist_retries': 3}, paper_version=True
        )
        print("fitting")
        tabpfn.fit(X_train[:20], y_train[:20], description=FULL_BREAST_CANCER_DESCRIPTION)
        print("predicting")
        print(tabpfn.predict(X_test))
        print("predicting_proba")
        print(tabpfn.predict_proba(X_test))
        print(f"last meta: {tabpfn.last_meta}")

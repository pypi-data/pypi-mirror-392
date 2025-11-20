# Obz AI - Copyright (C) 2025 Alethia XAI Sp. z o.o.
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, version 3.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.


from abc import ABC, abstractmethod
from typing import Optional
import numpy as np

# Dataclasses
from obzai.data_inspection.schemas.dataclasses import OutlierDetectionResults
# Exceptions
from obzai.data_inspection.schemas.exceptions import ODModelError


class _BaseODModel(ABC):
    """
    Base Outlier Detection Model class. 
    All inheriting classes have to implement ._fit_model() and ._score() methods.
    """
    def __init__(
        self,
        outlier_quantile: float = 0.01,
        higher_scores_normal: bool = True
        ) -> None:
        """
        Initialize an instance of base class. Should be called by an inheriting subclass.

        Args:
            outlier_quantile: A float value indicating outlier level threshold
            higher_scores_normal: A boolean flag indicating whether too high 
                or too low scores should be treated as outliers.
        """
        self.outlier_quantile = outlier_quantile
        self.higher_scores_normal = higher_scores_normal
        
        self._threshold: Optional[float] = None
        self._is_fitted: bool = False

    def fit(self, reference_features: np.ndarray) -> None:
        """
        Fits outlier detection model on a provided reference data
        and computes threshold for outlier classification.

        Args:
            reference_features - A numpy.ndarray of shape N x H with H reference features for N examples.
        """
        # (1) Sanity Checks of provided input
        self._input_features_sanity_check(reference_features)

        # (2) Run subclass specific fitting method on reference features
        try:
            self._fit_model(reference_features)
        except Exception as e:
            raise ODModelError(f"The error occured during fitting an outlier detection model: {e}")
        
        # (3) Run subclass specific scoring method on reference features
        try:
            scores = self._score(reference_features)
        except Exception as e:
            raise ODModelError(f"The error occured during scoring feature vectors: {e}")
        
        # (4) Check format of outliers, setup an outlier threshold and mark instance as fitted
        self._outlier_scores_sanity_check(scores)
        target = scores if self.higher_scores_normal else -scores
        self._threshold = float(np.quantile(target, self.outlier_quantile))
        self._is_fitted = True

    def predict(self, image_features: np.ndarray) -> OutlierDetectionResults:
        """
        Make prediction on provided batch of features, whether they correspond
        to outliers.

        Args:
            image_features: Batch of extracted, normalized features. Provided as numpy ndarray.

        Returns:
            OutlierDetectionResults: A dataclass containing detection results and scores 
        """
        # (1) Check whether instance is fitted
        if not self._is_fitted:
            raise RuntimeError("Model is not fitted.")

        # (2) Perform sanity check on provided input
        self._input_features_sanity_check(image_features)

        # (3) Score feature vectors with outlier score
        try:
            scores = self._score(image_features)
        except Exception as e:
            raise ODModelError(f"An error occured during scoring samples: {e}")

        # (4) Classify feature vectors as anomalous utilizing a threshold
        target = scores if self.higher_scores_normal else -scores
        outliers = (target < self._threshold)

        # (5) Return a standarized dataclass containing both classificiation results and scores
        return OutlierDetectionResults(
            outliers=outliers.tolist(),
            scores=scores.tolist()
            )

    @abstractmethod
    def _fit_model(self, image_features: np.ndarray) -> None:
        """
        Model specific fitting logic. Should be implemented by subclasses.
        It has to accept a numpy ndarray of shape NxH,
        where N is the number of samples and H is number of features in each feature vector.
        """
        pass

    @abstractmethod
    def _score(self, image_features: np.ndarray) -> np.ndarray:
        """
        Model specific inference/scoring logic. Should be implemented by subclasses.
        It has to accept a numpy ndarray of shape NxH,
        where N is the number of samples and H is number of features in each feature vector.
        It should return a numpy ndarray of shape (N,), i.e. single vector with float values
        corresponding to the outlier scores.
        """
        pass

    @staticmethod
    def _input_features_sanity_check(input_features: np.ndarray) -> None:
        """
        Method checks whether provided input features have valid format.
        
        Args:
            input_features: a numpy ndarray containing in each row feature vectors.
        
        Raises:
            ODModelError: When provided argument doesn't meet requirements.
        """
        if not isinstance(input_features, np.ndarray):
            raise ODModelError("Expected provided argument to be a numpy.ndarray.")
    
    @staticmethod
    def _outlier_scores_sanity_check(outlier_scores: np.ndarray) -> None:
        """
        Abstract method ._score() is expected to return a numpy ndarray
        with outlier scores. It should be single vector of shape (N,)
        where N is a number of examples.

        Args:
            outlier_scores: a numpy ndarray corresponding to outlier scores
        
        Raises:
            ODModelError: Raised when provided object doesn't meet requirements
        """
        if not isinstance(outlier_scores, np.ndarray):
            raise ODModelError("The abstract method ._score() is expected to return a numpy ndarray with outlier scores.")




# Obz AI - Copyright (C) 2025 Alethia XAI Sp. z o.o.
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, version 3.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.


from typing import Iterable, Dict, Any, List, Optional
from abc import ABC, abstractmethod
import pandas as pd
import uuid
import os

# Feature Pipeline
from obzai.data_inspection.feature_pipeline import FeaturePipeline

# OD Model base class (for typing)
from obzai.data_inspection.od_models.base_od_model import _BaseODModel

# Dataclasses, Types & Exceptions 
from obzai.data_inspection.schemas.dataclasses import (ImageFeatures, ReferenceData, 
                                                       DataInspectionResults, DataInspectorMeta)
from obzai.data_inspection.schemas.exceptions import DataInspectorError
from obzai.data_inspection.schemas.types import TensorOrSequenceOrDict
from obzai.data_inspection.schemas.types import FeatureType


from typing import Literal

# To remove annoying, scikit-learn internal warnings related to deprecation.
import warnings
warnings.filterwarnings(
    "ignore",
    message=".*'force_all_finite' was renamed to 'ensure_all_finite'.*",
    category=FutureWarning,
    module="sklearn"
)


class _BaseDataInspector(ABC):
    """
    Base class implementing key methods of Data Inspector. 
    It provides robust skeleton for all inheriting variants of Data Inspectors.
    """
    def __init__(
        self,
        feature_pipeline: FeaturePipeline,
        od_model: _BaseODModel
        ) -> None:
        """
        Initialize an instance of Data Inspector.
        In particular generate instance-specific ID of Data Inspector
        and ensure that .obz directory is created at current working directory.
        
        Args:
            feature_pipeline: Instance of a feature pipeline
            od_model: Instance of an outlier detection model
        """
        # Feature Pipeline & Outlier Detection model
        self.feature_pipeline = feature_pipeline
        self.od_model = od_model
        
        # Helper attributes
        self._id = self._generate_unique_id()
        self._is_fitted = False

        # Setup Obz Directory
        self._setup_obz_directory()
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Name of a Data Inspector.
        """
        ...

    @property
    @abstractmethod
    def logged_feature_type(self) -> FeatureType:
        """
        Type of logged feature type.
        """
        ...

    @property
    @abstractmethod
    def feature_names(self) -> Optional[List[str]]:
        """
        Returns the feature names for the feature pipeline.
        """
        ...

    @property
    @abstractmethod
    def hyperparams(self) -> Dict[str, Any]:
        """
        Hyperparameters of Data Inspector.
        """
        ...

    @property
    def id(self) -> str:
        """
        Returns the unique identifier for this inspector instance.
        """
        return self._id
    
    @property
    def metadata(self) -> DataInspectorMeta:
        """
        Returns metadata of that specific Data Inspector Instance.
        """
        return DataInspectorMeta(
            local_id=self._id,
            name=self.name,
            feature_type=self.logged_feature_type,
            feature_names=self.feature_names,
            hyperparams=self.hyperparams
        )

    def _generate_unique_id(self) -> str:
        """
        Generate a unique identifier that includes the class name and a UUID.
        """
        return f"{uuid.uuid4()}"

    def _setup_obz_directory(self) -> None:
        """
        Creates a directory containing Data Inspector related data.
        """
        self._root_dir = os.path.join(os.getcwd(), ".obz", self._id)
        os.makedirs(self._root_dir, exist_ok=True)

    def _save_reference_features(self, reference_features: ImageFeatures) -> None:
        """
        Saves reference features in the .obz directory located at current working directory.

        Args:
            reference_features: A dataclass containing raw, normalize and optionally projected image features.
        """
        # (1) Ensure that reference dir is located under .obz dir
        save_path = os.path.join(self._root_dir, "reference")
        os.makedirs(save_path, exist_ok=True)
        
        # (2) Save raw and normalized features
        raw_features_df = pd.DataFrame(reference_features.raw_features, columns=reference_features.feature_names)
        norm_features_df = pd.DataFrame(reference_features.norm_features, columns=reference_features.feature_names)

        raw_features_df.to_parquet(os.path.join(save_path, "ref_raw.parquet"), index=False)
        norm_features_df.to_parquet(os.path.join(save_path, "ref_norm.parquet"), index=False)

        # (3) Save 2D projections if available
        if reference_features.pca_projections is not None and reference_features.umap_projections is not None:
            pca_projections_df = pd.DataFrame(reference_features.pca_projections, columns=["x_coor", "y_coor"])
            umap_projections_df = pd.DataFrame(reference_features.umap_projections, columns=["x_coor", "y_coor"])

            pca_projections_df.to_parquet(os.path.join(save_path, "ref_pca_proj.parquet"), index=False)
            umap_projections_df.to_parquet(os.path.join(save_path, "ref_umap_proj.parquet"), index=False)

    def load_reference_data(self) -> ReferenceData:
        """
        Loads reference data stored under `reference` directory in .obz dir.

        Returns:
            ref_data: Objects containing loaded image features and if available correspoding 2D projections
        """
        # (1) Checks whether Data Inspector instance was already fitted. If not, reference data cannot be loaded.
        if not self._is_fitted:
            raise DataInspectorError("Inspector should be first fitted on reference data.")
        
        # (2) Path to directory storing reference features
        storage_path = os.path.join(self._root_dir, "reference")

        # (3) Try to load raw and normalized reference features
        try:
            raw_features = pd.read_parquet(os.path.join(storage_path, "ref_raw.parquet"))
            norm_features = pd.read_parquet(os.path.join(storage_path, "ref_norm.parquet"))
        except FileNotFoundError as e:
            raise DataInspectorError(f"Reference data not found: {e}")

        # (4) Try to load 2D projections of features if available
        try:
            pca_projections = pd.read_parquet(os.path.join(storage_path, "ref_pca_proj.parquet"))
            umap_projections = pd.read_parquet(os.path.join(storage_path, "ref_umap_proj.parquet"))
        except FileNotFoundError:
            pca_projections, umap_projections = None, None

        # (5) Return reference data (both features and projections) in a standardized way
        return ReferenceData(
            inspector_id     = self._id,
            feature_type     = self.logged_feature_type,
            raw_features     = raw_features,
            norm_features    = norm_features,
            pca_projections  = pca_projections,
            umap_projections = umap_projections
            )

    def fit(self, reference_images: Iterable[TensorOrSequenceOrDict]) -> None:
        """
        Extracts image features and fit outlier detection model.
        Saves extracted features in current working directory in the .obz/<Data Inspector ID> directory.

        Args:
            reference_images: Reference images might be provided as an Iterable returning:
                (i) a simple torch.Tensor of shape (B, C, H, W) or (B, C, D, H, W);
                (ii) a tuple[torch.Tensor, ...] or a list[torch.Tensor, ...] containing images at the first position;
                (iii) a dict[str, torch.Tensor | Any] containing images under key `images`.
        """
        # (1) Setup a feature pipeline
        ref_features = self.feature_pipeline.setup(reference_images)
        
        # (2) Save extracted reference features
        self._save_reference_features(ref_features)

        # (3) Fit OD model on normalized reference features
        self.od_model.fit(ref_features.norm_features)
        self._is_fitted = True

    def inspect(self, input_images: TensorOrSequenceOrDict) -> DataInspectionResults:
        """
        Extracts image features from a batch of input images and performs outlier detection.

        Args:
            input_images: Batch of input images provided in the following forms:
                (i) a simple torch.Tensor of shape (B, C, H, W) or (B, C, D, H, W);
                (ii) a tuple[torch.Tensor, ...] or a list[torch.Tensor, ...] containing images at the first position;
                (iii) a dict[str, torch.Tensor | Any] containing images under key `images`.

        Raises:
            DataInspectorError - Raises an error when any error occurs.
        
        Returns:
            DataInspectionResults - Object containing results of Data Inspections and extracted on the fly image features.
        """
        # (1) Checks whether Data Inspector instance was already fitted.
        if not self._is_fitted:
            raise DataInspectorError("Inspector should be first fitted on reference data.")
        
        # (2) Extracts image features
        try:
            image_features = self.feature_pipeline.run_pipeline(input_images)
        except Exception as e:
            raise DataInspectorError("Features extraction failed!") from e
        
        # (3) Performs outlier detection.
        try:
            outlier_detection_results = self.od_model.predict(image_features.norm_features)
        except Exception as e:
            raise DataInspectorError("Fitting an OD model failed!") from e  

        return DataInspectionResults(
            inspector_id     = self._id,
            outliers         = outlier_detection_results.outliers,
            scores           = outlier_detection_results.scores,
            feature_type     = self.logged_feature_type,
            feature_names    = image_features.feature_names,
            raw_features     = image_features.raw_features,
            norm_features    = image_features.norm_features,
            pca_projections  = image_features.pca_projections,
            umap_projections = image_features.umap_projections
            )
# Obz AI - Copyright (C) 2025 Alethia XAI Sp. z o.o.
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, version 3.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.

from abc import abstractmethod
import numpy as np
import torch

from obzai.data_inspection.extractors.extractor import Extractor


class CustomExtractor(Extractor):
    """
    Abstract base class for a custom feature extractor.
    Subclasses must implement the .extract() method, which should accept a batch of images
    (torch.Tensor) and return a batch of feature vectors as a numpy array.
    
    Attributes:
        feature_names (list[str] or None): Names of the features extracted. Should be set by subclasses.
    """
    def __init__(self):
        super().__init__()
        self.id = 3
        self.name = self.__class__.__name__
        self.feature_names = None  # Should be set by subclass if known

    @abstractmethod
    def extract(self, image_batch: torch.Tensor) -> np.ndarray:
        """
        Extract features from a batch of images.
        Args:
            image_batch (torch.Tensor): Batch of images (B, C, H, W).
        Returns:
            np.ndarray: Batch of feature vectors (B, F).
        """
        pass
# Obz AI - Copyright (C) 2025 Alethia XAI Sp. z o.o.
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, version 3.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.

import torchvision.transforms.v2.functional as F
from abc import ABC, abstractmethod
from typing import Sequence
import numpy as np
import torch


class Extractor(ABC):
    def __init__(self):
        self.id: int = None
        self.name: str = None

    def _process_batch(self, 
                       batch: torch.Tensor,
                       image_size: int|Sequence[int] = 224,
                       ensure_grayscale: bool = False,
                       ensure_scale: bool=True) -> torch.Tensor:
        """
        Method accepts a torch.Tensor batch of images and processes it by resizing, optionaly grey scaling.
        Parameters:
            image: Input image as a torch.Tensor of shape (B, C, H, W) or (B, 1, H, W) if grayscale.
        """
        batch = batch.cpu()

        # Ensure proper DataType and scale:
        if ensure_scale:
            batch = F.to_dtype(batch, dtype=torch.float32, scale=True)

        # Resizing the image into a specified size
        if isinstance(image_size, int):
            image_size = [image_size, image_size]
        batch = F.resize(batch, size=image_size)
        
        # Convert RGB image to grayscale (if needed)
        if ensure_grayscale:
            F.rgb_to_grayscale(batch)
        
        return batch
    
    @abstractmethod
    def extract(self, image_batch: torch.Tensor) -> np.ndarray:
        """
        Method implements a custom loop over batch during features extraction.
        """
        pass
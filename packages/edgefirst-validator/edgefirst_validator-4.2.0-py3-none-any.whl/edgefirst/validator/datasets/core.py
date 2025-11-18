"""
Common parent dataset implementations.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Union, Tuple

import numpy as np
import tqdm

from edgefirst.validator.datasets.utils.readers import read_image
from edgefirst.validator.datasets.utils.transformations import (xcycwh2xyxy,
                                                                xywh2xyxy,
                                                                normalize,
                                                                denormalize_polygon)

if TYPE_CHECKING:
    from edgefirst.validator.evaluators import DatasetParameters, TimerContext
    from edgefirst_python import TensorImage  # type: ignore

    from edgefirst.validator.datasets import (
        SegmentationInstance, DetectionInstance, MultitaskInstance, Instance)


class Dataset:
    """
    Abstract dataset class for providing template methods in the dataset.

    Parameters
    ----------
    source: str
        The path to the source dataset.
    parameters: DatasetParameters
        This contains dataset parameters set from the command line.
    timer: TimerContext
        A timer object for handling validation timings for the model.
    info_dataset: dict
        Contains information such as:

            .. code-block:: python

                {
                    "classes": [list of unique labels],
                    "validation":
                    {
                        "images: 'path to the images',
                        "annotations": 'path to the annotations'
                    }
                }

        *Note: the classes are optional and the path to the images
        and annotations can be the same.*

    Raises
    ------
    ValueError
        Raised if the provided parameters in certain methods
        does not conform to the specified data type.
    """

    def __init__(
        self,
        source: str,
        parameters: DatasetParameters,
        timer: TimerContext,
        info_dataset: dict = None
    ):
        self.source = source
        self.parameters = parameters
        self.timer = timer
        self.info_dataset = info_dataset
        self.samples = []

        self.transformer = None
        if self.parameters.box_format == 'xcycwh':
            self.transformer = xcycwh2xyxy
        elif self.parameters.box_format == 'xywh':
            self.transformer = xywh2xyxy
        else:
            self.transformer = None

        self.normalizer = None
        self.denormalizer = None
        if self.parameters.normalized:
            if self.parameters.common.with_masks:
                self.denormalizer = denormalize_polygon
        else:
            if self.parameters.common.with_boxes:
                self.normalizer = normalize

    def __len__(self) -> int:
        """
        Returns the number of samples in the dataset.
        """
        return len(self.samples)

    def __iter__(self):
        """
        Reads all the samples in the dataset.

        Yields
        -------
        Instance
            Yields one sample of the ground truth
            instance which contains information on the image
            as a NumPy array, boxes, labels, and image path.
        """
        if self.parameters.silent:
            samples = self.collect_samples()
            for sample in samples:
                yield self.read_sample(sample)
        else:
            samples = tqdm.tqdm(self.collect_samples(), colour="green")
            samples.set_description("Validation Progress")
            for sample in samples:
                yield self.read_sample(sample)

    def verify_dataset(self):
        """Abstract Method"""
        pass

    def read_sample(self,
                    sample: Union[list, Tuple[str, str], str]) -> Instance:
        """
        Reads one sample from the dataset.

        Parameters
        -----------
        sample: Union[list, Tuple[str, str], str]
            For EdgeFirstDatabase, this is a list. For Darknet datasets,
            this is a Tuple[str, str] containing the path to the image
            and annotations. For dataset cache, this is a string
            as the image name.

            A single dataset sample contains the indices
            in the dataframe pointing to all the annotations
            in the dataset for this sample.

        Returns
        -------
        Instance
            The ground truth instance objects contains the annotations
            representing the ground truth of the image.
        """
        if self.parameters.common.with_boxes and self.parameters.common.with_masks:
            return self.build_multitask_instance(sample)
        elif self.parameters.common.with_boxes:
            return self.build_detection_instance(sample)
        elif self.parameters.common.with_masks:
            return self.build_segmentation_instance(sample)
        else:
            raise ValueError(
                "Could not determine model task as detection or segmentation.")

    def load_image(
        self,
        image_path: str,
        backend: str = "hal"
    ) -> Union[TensorImage, np.ndarray]:
        """
        Load the image into memory using various libraries: "hal", "opencv",
        or "pillow".

        Parameters
        ----------
        image_path: str
            The path to the image.
        backend: str
            Specify the backend library for resizing the image
            from the options "hal", "opencv", "pillow".

        Returns
        -------
        Union[edgefirst_python.TensorImage, np.ndarray]
            TensorImage is returned when using "hal". Otherwise, a
            NumPy array is returned.
        """

        if backend == "hal":
            try:
                import edgefirst_python  # type: ignore
            except ImportError:
                raise ImportError(
                    "EdgeFirst HAL is needed to read the image.")
            # Read the image.
            return edgefirst_python.TensorImage.load(
                image_path, fourcc=edgefirst_python.FourCC.RGBA)
        elif backend == "opencv":
            try:
                import cv2  # type: ignore
            except ImportError:
                raise ImportError("OpenCV is needed to read the image.")

            return cv2.imread(image_path)
        else:
            return read_image(image_path, rotate=True)

    def image(self, sample: Union[tuple, list]):
        """Abstract Method"""
        raise NotImplementedError("Abstract Method")

    def labels(self, sample: Union[tuple, list]) -> np.ndarray:
        """
        Fetch the labels of the specified sample.

        Parameters
        ----------
        sample: Union[tuple, list]
            A tuple containing the (image path, annotation path) or
            a list of indices in the polars dataframe for the current sample.

        Returns
        -------
        np.ndarray
            The labels in the sample containing np.int32 elements.
        """
        return np.array([])

    def boxes(self, index: int) -> np.ndarray:
        """Abstract Method"""
        raise NotImplementedError("Abstract Method")

    def mask(self, index: int) -> np.ndarray:
        """Abstract Method"""
        raise NotImplementedError("Abstract Method")

    def segments(self, index: int) -> np.ndarray:
        """Abstract Method"""
        raise NotImplementedError("Absract Method")

    def name(self, index: int) -> str:
        """Abstract Method"""
        raise NotImplementedError("Abstract Method")

    def collect_samples(self):
        """Abstract Method"""
        raise NotImplementedError("This is an abstract method.")

    def build_detection_instance(self, sample: list) -> DetectionInstance:
        """Abstract Method"""
        pass

    def build_segmentation_instance(
            self, sample: list) -> SegmentationInstance:
        """Abstract Method"""
        pass

    def build_multitask_instance(self, sample: list) -> MultitaskInstance:
        """Abstract Method"""
        pass

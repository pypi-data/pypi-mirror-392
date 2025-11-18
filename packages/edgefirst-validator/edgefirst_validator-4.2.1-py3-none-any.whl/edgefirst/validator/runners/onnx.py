from __future__ import annotations

import os
import time
import ctypes
from typing import TYPE_CHECKING, Any

import numpy as np

from edgefirst.validator.publishers.utils.logger import logger
from edgefirst.validator.runners.core import Runner

if TYPE_CHECKING:
    from edgefirst.validator.evaluators import ModelParameters, TimerContext


class ONNXRunner(Runner):
    """
    Loads and runs ONNX models for inference.

    Parameters
    ----------
    model: Any
        This is typically the path to the model (.onnx)
        or the loaded ONNX model.
    parameters: ModelParameters
        These are the model parameters set from the command line.
    metadata: dict
        The model metadata which contains information for decoding
        the model outputs.
    timer: TimerContext
        A timer object for handling validation timings for the model.

    Raises
    ------
    ImportError
        Missing onnxruntime library.
    FileNotFoundError
        Raised if the path to the model does not exist.
    """

    def __init__(
        self,
        model: Any,
        parameters: ModelParameters,
        metadata: dict,
        timer: TimerContext
    ):
        super(ONNXRunner, self).__init__(model, parameters, timer=timer)

        try:
            import onnxruntime
        except ImportError:
            raise ImportError(
                "onnxruntime or onnxruntime-gpu is needed to run ONNX models.")

        if isinstance(model, str):
            if not os.path.exists(model):
                raise FileNotFoundError(
                    "The model '{}' does not exist.".format(model))

            providers = self.select_providers()
            logger(f"Selected Providers: {providers}", code="INFO")
            self.model = onnxruntime.InferenceSession(
                model, providers=providers)

        self.graph_name = self.model.get_modelmeta().graph_name
        self.output_names = [x.name for x in self.model.get_outputs()]
        outputs = self.model.get_outputs()
        self.init_decoder(metadata=metadata, outputs=outputs)

        if self.parameters.warmup > 0:
            self.warmup()

    @staticmethod
    def check_tensorrt_runtime() -> list:
        """
        The following libraries are needed to run ONNX
        with TensorrtExecutionProvider.

        - "libnvinfer.so"
        - "libnvinfer_plugin.so"
        - "libnvonnxparser.so"

        Returns
        -------
        list
            A list of the libraries that are missing.
        """
        required_libs = ["libnvinfer.so",
                         "libnvinfer_plugin.so", "libnvonnxparser.so"]
        missing = []
        for lib in required_libs:
            try:
                ctypes.CDLL(lib)
            except OSError:
                missing.append(lib)
        return missing

    def select_providers(self) -> list:
        """
        Specify the providers to load based on
        the type of engine specified.

        Returns
        -------
        list
            A list of the selected providers to deploy.
        """
        import onnxruntime

        selected_providers = ["CPUExecutionProvider"]
        available_providers = onnxruntime.get_available_providers()
        if self.parameters.engine.lower() == "npu":
            preferred_providers = ["NnapiExecutionProvider",
                                   "VsiNpuExecutionProvider",
                                   "TensorrtExecutionProvider",
                                   "CUDAExecutionProvider",
                                   "CPUExecutionProvider"]
            selected_providers = []
            for i, provider in enumerate(preferred_providers):
                if provider in available_providers:
                    if provider == "TensorrtExecutionProvider":
                        missing_libraries = self.check_tensorrt_runtime()
                        if missing_libraries:
                            logger(f"The libraries {missing_libraries} are " +
                                   "needed for TensorrtExecutionProvider. " +
                                   f"Falling back to {preferred_providers[i+1]}.",
                                   code="WARNING")
                            continue
                    selected_providers.append(provider)
                else:
                    logger(f"{provider} is not present in the system. " +
                           f"Falling back to {preferred_providers[i+1]}.",
                           code="WARNING")
            if selected_providers in [["TensorrtExecutionProvider",
                                       "CUDAExecutionProvider",
                                       "CPUExecutionProvider"],
                                      ["CUDAExecutionProvider",
                                       "CPUExecutionProvider"]]:
                self.parameters.engine = "gpu"
            elif selected_providers == ["CPUExecutionProvider"]:
                self.parameters.engine = "cpu"
        elif self.parameters.engine.lower() == "gpu":
            preferred_providers = ["TensorrtExecutionProvider",
                                   "CUDAExecutionProvider",
                                   "CPUExecutionProvider"]
            selected_providers = []
            for i, provider in enumerate(preferred_providers):
                if provider in available_providers:
                    if provider == "TensorrtExecutionProvider":
                        missing_libraries = self.check_tensorrt_runtime()
                        if missing_libraries:
                            logger(f"The libraries {missing_libraries} are " +
                                   "needed for TensorrtExecutionProvider. " +
                                   f"Falling back to {preferred_providers[i+1]}.",
                                   code="WARNING")
                            continue
                    selected_providers.append(provider)
                else:
                    logger(f"{provider} is not present in the system. " +
                           f"Falling back to {preferred_providers[i+1]}.",
                           code="WARNING")
            if selected_providers == ["CPUExecutionProvider"]:
                self.parameters.engine = "cpu"
                logger(
                    "TensorrtExecutionProvider and CUDAExecutionProvider is " +
                    "not present in the system. Falling back to CPUExecutionProvider.",
                    code="WARNING")
        return selected_providers

    def run_single_instance(self, image: np.ndarray) -> Any:
        """
        Run ONNX inference on a single image and record the timings.

        Parameters
        ----------
        image: np.ndarray
            The input image after being preprocessed.
            Typically this is an RGB image array.

        Returns
        -------
        Any
            This could either return detection outputs after NMS.
                np.ndarray
                    The prediction bounding boxes.. [[box1], [box2], ...].
                np.ndarray
                    The prediction labels.. [cl1, cl2, ...].
                np.ndarray
                    The prediction confidence scores.. [score, score, ...]
                    normalized between 0 and 1.
            This could also return segmentation masks.
                np.ndarray
        """
        # Inference
        with self.timer.time("inference"):
            outputs = self.model.run(self.output_names,
                                     {self.model.get_inputs()[0].name: image})

        # Postprocessing
        return self.postprocessing(outputs)

    def get_input_type(self) -> np.dtype:
        """
        This returns the input type of the model for the
        input with shape in the form
        (batch size, channels, height, width) or
        (batch size, height, width, channels).

        Returns
        -------
        np.dtype
            The input type of the model.
        """
        if "float16" in self.model.get_inputs()[0].type:
            return np.float16
        elif "float" in self.model.get_inputs()[0].type:
            return np.float32
        elif "uint8" in self.model.get_inputs()[0].type:
            return np.uint8
        elif "int8" in self.model.get_inputs()[0].type:
            return np.int8
        return self.model.get_inputs()[0].type

    def get_input_shape(self) -> np.ndarray:
        """
        This fetches the model input shape.

        Returns
        -------
        np.ndarray
            The model input shape
            (batch size, channels, height, width) or
            (batch size, height, width, channels).
        """
        for input in self.model.get_inputs():
            if len(input.shape) == 4:
                if input.shape[1] == 3 or input.shape[-1] == 3:
                    return input.shape
        return self.model.get_inputs()[0].shape

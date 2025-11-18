from __future__ import annotations
from typing import TYPE_CHECKING, Any, Union, Tuple, List
import time

import numpy as np
import numpy.typing as npt

from edgefirst.validator.datasets.utils.transformations import (xyxy2xcycwh,
                                                                xcycwh2xyxy,
                                                                xyxy2xywh,
                                                                resize,
                                                                preprocess_hal,
                                                                preprocess_native)
from edgefirst.validator.runners.processing.decode import (decode_mpk_boxes,
                                                           decode_mpk_masks,
                                                           decode_yolo_boxes,
                                                           decode_yolo_masks,
                                                           decode_yolox_boxes,
                                                           crop_masks,
                                                           dequantize)
from edgefirst.validator.runners.processing.nms import nms, multiclass_nms
from edgefirst.validator.datasets.utils.fetch import get_shape
from edgefirst.validator.publishers.utils.logger import logger
from edgefirst.validator.runners.processing.outputs import Outputs

if TYPE_CHECKING:
    from edgefirst.validator.evaluators import ModelParameters, TimerContext

DetOutput = Tuple[npt.NDArray[np.float32],
                  npt.NDArray[np.float32], npt.NDArray[np.uintp]]
SegDetOutput = Tuple[npt.NDArray[np.float32],
                     npt.NDArray[np.float32],
                     npt.NDArray[np.uintp],
                     Union[None, npt.NDArray[np.uint8],
                           List[npt.NDArray[np.uint8]]]]


class Runner:
    """
    Abstract class that provides a template for the other runner classes.

    Parameters
    ----------
    model: Any
        This is typically the path to the model file or a loaded model.
    parameters: Parameters
        These are the model parameters set from the command line.
    timer: TimerContext
        A timer object for handling validation timings for the model.

    Raises
    ------
    FileNotFoundError
        Raised if the path to the model does not exist.
    """

    def __init__(self, model: Any, parameters: ModelParameters,
                 timer: TimerContext):
        self.model = model
        self.parameters = parameters
        self.timer = timer

        self.num_boxes = 0  # The number of boxes in the model output shape.
        self.graph_name = "main_graph"
        self.outputs = None
        self.decoder = None

    def init_decoder(
            self, metadata: dict, outputs: Union[List[dict], List[np.ndarray]]):
        """
        Parse the model metadata and initialize the HAL decoder.

        Parameters
        ----------
        metadata: dict
            The contents of the model metadata for decoding the outputs.
        outputs: Union[List[dict], List[np.ndarray]]
            This is either a List[dict] from a TFLite output details
            or a List[np.ndarray] containing the shapes from the model outputs.
        """
        self.type = self.get_input_type()
        shape = self.get_input_shape()
        # Avoid shape [None, height, width, 3]
        self.shape = np.array([d if d is not None else 1 for d in shape])

        # Transpose the image to meet requirements of the channel order.
        if shape[-1] in [2, 3, 4]:
            height, width = shape[1:3]
            channels = shape[-1]
        else:
            height, width = shape[2:4]
            channels = shape[1]
            self.parameters.common.transpose = True

        self.parameters.common.dtype = self.type
        self.parameters.common.shape = self.shape

        # Parse the model output details in the metadata.
        self.outputs = Outputs(
            metadata=metadata,
            parameters=self.parameters,
            outputs=outputs
        )

        if self.parameters.nms == "hal":
            try:
                import edgefirst_python  # type: ignore
                self.decoder = edgefirst_python.Decoder(
                    self.outputs.metadata,
                    score_threshold=self.parameters.score_threshold,
                    iou_threshold=self.parameters.iou_threshold
                )
            except ImportError:
                raise ImportError(
                    "EdgeFirst HAL is needed to perform decoding using hal."
                )

        if self.parameters.common.backend == "hal":
            try:
                import edgefirst_python  # type: ignore
                if self.parameters.common.transpose:
                    if channels == 2:
                        raise NotImplementedError(
                            "NV16 format is currently not supported in HAL for " +
                            f"model input shape: {self.shape}")
                    elif channels == 4:
                        logger(
                            "PLANAR_RGBA is currently not supported in HAL for " +
                            f"model input shape: {self.shape}", code="WARNING"
                        )
                    fourcc = edgefirst_python.FourCC.PLANAR_RGB
                else:
                    if channels == 2:
                        fourcc = edgefirst_python.FourCC.YUYV
                    else:
                        fourcc = edgefirst_python.FourCC.RGBA
                self.parameters.common.input_dst = edgefirst_python.TensorImage(
                    width, height, fourcc
                )
            except ImportError:
                raise ImportError(
                    "EdgeFirst HAL is needed to perform preprocessing using hal."
                )

    def warmup(self):
        """
        Run model warmup.
        """

        logger("Running model warmup...", code="INFO")

        times = []
        height, width = get_shape(self.shape)

        for _ in range(self.parameters.warmup):
            start = time.perf_counter()
            # Warmup input preprocessing.
            if self.parameters.common.backend == "hal":
                import edgefirst_python  # type: ignore
                image, _, _, _ = preprocess_hal(
                    image=edgefirst_python.TensorImage(width, height),
                    shape=self.shape,
                    input_type=self.type,
                    dst=self.parameters.common.input_dst,
                    input_tensor=self.parameters.common.input_tensor,
                    transpose=self.parameters.common.transpose,
                    preprocessing=self.parameters.common.preprocessing,
                    normalization=self.parameters.common.norm,
                    quantization=self.parameters.common.input_quantization,
                )
            else:
                image, _, _, _ = preprocess_native(
                    image=np.zeros((height, width, 3), dtype=np.uint8),
                    shape=self.shape,
                    input_type=self.type,
                    input_tensor=self.parameters.common.input_tensor,
                    transpose=self.parameters.common.transpose,
                    preprocessing=self.parameters.common.preprocessing,
                    normalization=self.parameters.common.norm,
                    quantization=self.parameters.common.input_quantization,
                    backend=self.parameters.common.backend,
                )
            self.run_single_instance(image)

            elapsed = time.perf_counter() - start
            times.append(elapsed * 1e3)  # Convert to ms

        message = "model warmup took %f ms (%f ms avg)" % (np.sum(times),
                                                           np.average(times))
        logger(message, code="INFO")
        self.timer.reset()

    def run_single_instance(self, image: Union[str, np.ndarray]) -> Any:
        """Abstract Method"""
        pass

    def postprocessing(self, outputs: Union[list, np.ndarray]) -> Any:
        """
        Postprocess outputs into boxes, scores, labels or masks.
        This method will perform NMS operations where the outputs
        will be transformed into the following format.

        Models trained using ModelPack separates the outputs and
        directly return the NMS bounding boxes, scores, and
        labels as described below.

        Models converted in YOLOv5 will be a list of length 1 which
        has a shape of (1, number of boxes, 6) and formatted as
        [[[xmin, ymin, xmax, ymax, confidence, label], [...], ...]].

        Models converted in YOLOv7 will directly extract the
        bounding boxes, scores, and labels from the output.

        Parameters
        ----------
        outputs: Union[list, np.ndarray]
            ModelPack outputs will be a list with varying lengths
            which could either contain bounding boxes, labels, scores,
            or masks (encoded and decoded).

            Models converted in YOLOv5 has the following shape
            (batch size, number of boxes, number of classes).

            Models converted in YOLOv7 will already have NMS embedded. The
            output has a shape of (number of boxes, 7) and formatted as
            [[batch_id, xmin, ymin, xmax, ymax, cls, score], ...].

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
        # MobileNet SSD
        if self.outputs.classes["index"] is not None:
            with self.timer.time("output"):
                output = outputs[0] if len(outputs) == 1 else outputs
                output = output.numpy() if not isinstance(
                    output, (np.ndarray, list)) else output

                boxes, classes, scores, _ = output
                boxes = np.squeeze(boxes)
                classes = np.squeeze(classes).astype(np.int32)
                scores = np.squeeze(scores)
        # ModelPack or Kinara
        elif len(self.outputs.mpk_types) or (None not in
                                             [self.outputs.boxes["index"],
                                              self.outputs.scores["index"]]):
            with self.timer.time("output"):
                # Kinara
                if self.outputs.boxes["decoder"] == "yolov8":
                    if self.parameters.nms == "hal":
                        boxes, scores, classes, masks = self.decoder.decode(
                            outputs)

                        h, w = get_shape(self.shape)
                        normalized_conf = np.mean((boxes >= 0) & (boxes <= 1))
                        if normalized_conf < 0.80:
                            boxes[:, [0, 2]] /= w
                            boxes[:, [1, 3]] /= h
                    else:
                        outputs = np.concatenate(outputs, axis=1)
                        # Process YOLOv8 detection with shape [1, 84, 8400].
                        boxes, classes, scores, masks = self.process_yolo(
                            [outputs])

                # ModelPack
                else:
                    if self.parameters.nms == "hal":
                        boxes, classes, scores, masks = self.process_mpk_hal(
                            outputs)
                    else:
                        boxes, classes, scores, masks = self.process_mpk(
                            outputs)
        else:
            # YOLOx
            if (self.graph_name not in ["main_graph", "torch_jit", "tf2onnx"]
                    and outputs[0].shape[-1] == 85):

                # HAL decoder/NMS is not yet supported and fallback to NumPy.
                if self.parameters.nms == "hal":
                    self.parameters.nms = "numpy"

                with self.timer.time("output"):
                    boxes, classes, scores = self.process_yolox(
                        outputs=outputs)

            # YOLOv5, YOLOv8, YOLOv11 models.
            else:
                with self.timer.time("output"):
                    # Decoded outputs.
                    if len(outputs) == 1 and outputs[0].shape == (1, 300, 6):
                        height, width = get_shape(self.shape)
                        output = outputs[0].squeeze()
                        scores = output[:, 4]
                        classes = output[:, 5]
                        boxes = output[:, 0:4]

                        # Filter out all zero rows.
                        filt = ~np.all(boxes[:, 0:4] == 0, axis=1)
                        boxes = boxes[filt]
                        scores = scores[filt]
                        classes = classes[filt]
                        # Normalize bounding boxes if not already.
                        if boxes.shape[0] > 0:
                            normalized_conf = np.mean(
                                (boxes >= 0) & (boxes <= 1))
                            if normalized_conf < 0.80:
                                boxes[..., [0, 2]] /= width
                                boxes[..., [1, 3]] /= height
                        # No masks from this output shape.
                        masks = None
                    elif self.parameters.nms == "hal":
                        boxes, classes, scores, masks = self.process_yolo_hal(
                            outputs)
                    else:
                        boxes, classes, scores, masks = self.process_yolo(
                            outputs)

        if self.parameters.common.with_boxes:
            if self.parameters.box_format == "xcycwh":
                boxes = xyxy2xcycwh(boxes)
            elif self.parameters.box_format == "xywh":
                boxes = xyxy2xywh(boxes)

            if self.parameters.label_offset != 0:
                classes += self.parameters.label_offset

            if self.parameters.common.with_masks:
                return boxes, classes, scores, masks
            else:
                return boxes, classes, scores
        else:
            return masks

    def process_mpk_hal(self, outputs: List[np.ndarray]):
        """
        ModelPack output decoding and postprocessing using the HAL decoder.

        Parameters
        ----------
        outputs: List[np.ndarray]
            ModelPack outputs will be a list with varying lengths
            which could either contain bounding boxes, labels, scores,
            or masks (encoded and decoded).

        Returns
        -------
        boxes : np.ndarray
            This contains decoded and valid bounding boxes post NMS.
        classes : np.ndarray
            This contains decoded and valid classes post NMS.
        scores : np.ndarray
            This contains decoded and valid scores post NMS.
        masks: np.ndarray
            This is the semantic segmentation mask output from
            ModelPack. If the model is not a segmentation model,
            None is returned.
        """
        masks = None
        for context in self.outputs.mpk_types:
            if context["type"] == "segmentation":
                masks = outputs[context["index"]]

        boxes, scores, classes, masks = self.decoder.decode(
            outputs, max_boxes=self.parameters.max_detections)

        height, width = get_shape(self.shape)
        # Decoded masks.
        if self.outputs.masks["index"] is not None:
            masks = np.squeeze(
                outputs[self.outputs.masks["index"]]).astype(np.uint8)
            # Resize the mask to the model input shape.
            masks = resize(masks, size=(width, height))
        # Deploy argmax to the mask and convert to semantic segmentation.
        elif len(masks):
            masks = self.decoder.segmentation_to_mask(masks[0])
            # Resize the mask to the model input shape.
            masks = resize(masks, size=(width, height))

        return boxes, classes, scores, masks

    def process_mpk(self, outputs: List[np.ndarray]) -> SegDetOutput:
        """
        ModelPack output decoding and postprocessing.

        Parameters
        ----------
        outputs: List[np.ndarray]
            ModelPack outputs will be a list with varying lengths
            which could either contain bounding boxes, labels, scores,
            or masks (encoded and decoded).

        Returns
        -------
        boxes : np.ndarray
            This contains decoded and valid bounding boxes post NMS.
        classes : np.ndarray
            This contains decoded and valid classes post NMS.
        scores : np.ndarray
            This contains decoded and valid scores post NMS.
        masks: np.ndarray
            This is the semantic segmentation mask output from
            ModelPack. If the model is not a segmentation model,
            None is returned.
        """

        output = outputs[0] if len(outputs) == 1 else outputs
        output = output.numpy() if not isinstance(
            output, (np.ndarray, list)) else output

        # Fetch only (height, width) from the shape.
        height, width = get_shape(self.shape)

        boxes, scores = [], []
        classes, masks = None, None
        for context in self.outputs.mpk_types:
            x = output[context["index"]]
            if context["quantization"] is not None and x.dtype != np.float32:
                x = dequantize(x, *context["quantization"])

            if context["type"] == "detection":
                box, score = decode_mpk_boxes(p=x, anchors=context["anchors"])
                boxes.append(box)
                scores.append(score)

            elif context["type"] == "segmentation":
                masks = np.squeeze(decode_mpk_masks(masks=x))
                masks = resize(masks, size=(width, height),
                               backend=self.parameters.common.backend)

        # The boxes and scores are already decoded.
        if None not in [self.outputs.boxes["index"],
                        self.outputs.scores["index"]]:

            boxes = output[self.outputs.boxes["index"]]
            if (self.outputs.boxes["quantization"] is not None and
                    boxes.dtype != np.float32):
                boxes = dequantize(boxes, *self.outputs.boxes["quantization"])

            scores = output[self.outputs.scores["index"]]
            if (self.outputs.scores["quantization"] is not None and
                    scores.dtype != np.float32):
                scores = dequantize(
                    scores, *self.outputs.scores["quantization"])

        if 0 not in [len(boxes), len(scores)]:
            scores = np.concatenate(scores, axis=1).astype(np.float32)
            boxes = np.concatenate(boxes, axis=1).astype(np.float32)
            if scores.shape[0] == 1:
                scores = np.squeeze(scores, axis=0)
            if boxes.shape[0] == 1:
                boxes = np.squeeze(boxes, axis=0)

            boxes, classes, scores, _ = nms(
                boxes=boxes,
                scores=scores,
                iou_threshold=self.parameters.iou_threshold,
                score_threshold=self.parameters.score_threshold,
                max_detections=self.parameters.max_detections,
                class_agnostic=self.parameters.agnostic_nms,
                nms_type=self.parameters.nms
            )

            # Normalize bounding boxes if not already.
            if boxes.shape[0] > 0:
                normalized_conf = np.mean((boxes >= 0) & (boxes <= 1))
                if normalized_conf < 0.80:
                    boxes[..., [0, 2]] /= width
                    boxes[..., [1, 3]] /= height

        # Decoded masks.
        if masks is None and self.outputs.masks["index"] is not None:
            masks = np.squeeze(
                output[self.outputs.masks["index"]]).astype(np.uint8)
            masks = resize(masks, size=(width, height),
                           backend=self.parameters.common.backend)

        return boxes, classes, scores, masks

    def process_yolo_hal(self, outputs: List[np.ndarray]) -> SegDetOutput:
        """
        Utralytics YOLO output decoding and postprocessing using the
        HAL decoder.

        Parameters
        ----------
        outputs: List[np.ndarray]
            Models converted in YOLOv5 has the following shape
            (batch size, number of boxes, number of classes) for detection.

            Models converted in YOLOv7 will already have NMS embedded. The
            output has a shape of (number of boxes, 7) and formatted as
            [[batch_id, xmin, ymin, xmax, ymax, cls, score], ...].

            For segmentation models, this will contain two arrays containing
            the detection and segmentation outputs.

        Returns
        -------
        boxes : np.ndarray
            This contains decoded and valid bounding boxes post NMS.
        classes : np.ndarray
            This contains decoded and valid classes post NMS.
        scores : np.ndarray
            This contains decoded and valid scores post NMS.
        masks: np.ndarray
            This is the instance segmentation mask outputs from
            Ultralytics. If the model is not a segmentation model,
            None is returned.
        """
        h, w = get_shape(self.shape)

        # NOTE: HAL Decoder requires normalized bounding boxes.
        x = outputs[self.outputs.scores["index"]]
        if x.shape[0] > 0 and x.dtype in [np.float32, np.float16]:
            normalized_conf = np.mean((x[:, :4, :] >= 0) & (x[:, :4, :] <= 1))
            if normalized_conf < 0.80:
                x[:, [0, 2], :] /= w
                x[:, [1, 3], :] /= h
                outputs[self.outputs.scores["index"]] = x

        # Transpose proto masks into the proper shape.
        # NOTE: HAL decoder requires shape [1, 160, 160, 32]
        if self.outputs.masks["index"] is not None:
            masks = outputs[self.outputs.masks["index"]]
            if masks.shape[1] == 32:
                outputs[self.outputs.masks["index"]] = np.transpose(
                    masks, (0, 2, 3, 1))

        boxes, scores, classes, masks = self.decoder.decode(
            outputs, max_boxes=self.parameters.max_detections
        )

        # Filter invalid 0-dimension boxes.
        valid = np.where((boxes[..., 0] < boxes[..., 2]) &
                         (boxes[..., 1] < boxes[..., 3]))[0]
        boxes = boxes[valid]
        scores = scores[valid]
        classes = classes[valid]
        if len(masks) > 0:
            masks = [masks[i] for i in valid]

        # Paint masks onto a fixed shape NumPy array canvas.
        full_masks = []
        for b, m in zip(boxes, masks):
            # Resize the mask into the input shape of the model.
            mask_width = round((b[2] - b[0]) * w)
            mask_height = round((b[3] - b[1]) * h)
            m = resize(m, size=(mask_width, mask_height))
            mask = np.zeros((w, h, 1), dtype=np.uint8)
            left = round(b[0] * w)
            top = round(b[1] * h)
            mask[top:(top + mask_height), left:(left + mask_width), 0] = m

            # Run Argmax on the masks.
            mask = self.decoder.segmentation_to_mask(mask)
            full_masks.append(mask)

        if len(full_masks):
            masks = np.stack(full_masks, axis=0)
        return boxes, classes, scores, masks

    def process_yolo(self, outputs: List[np.ndarray]) -> SegDetOutput:
        """
        Utralytics YOLO output decoding and postprocessing.

        Parameters
        ----------
        outputs: List[np.ndarray]
            Models converted in YOLOv5 has the following shape
            (batch size, number of boxes, number of classes) for detection.

            Models converted in YOLOv7 will already have NMS embedded. The
            output has a shape of (number of boxes, 7) and formatted as
            [[batch_id, xmin, ymin, xmax, ymax, cls, score], ...].

            For segmentation models, this will contain two arrays containing
            the detection and segmentation outputs.

        Returns
        -------
        boxes : np.ndarray
            This contains decoded and valid bounding boxes post NMS.
        classes : np.ndarray
            This contains decoded and valid classes post NMS.
        scores : np.ndarray
            This contains decoded and valid scores post NMS.
        masks: np.ndarray
            This is the instance segmentation mask outputs from
            Ultralytics. If the model is not a segmentation model,
            None is returned.
        """
        output = outputs[0] if len(outputs) == 1 else outputs
        output = output.numpy() if not isinstance(
            output, (np.ndarray, list)) else output

        # Fetch only (height, width) from the shape.
        h, w = get_shape(self.shape)

        x = output[self.outputs.scores["index"]]
        if x.dtype == np.float16:
            x = x.astype(np.float32)
        if (self.outputs.scores["quantization"] is not None and
                x.dtype != np.float32):
            x = dequantize(x, *self.outputs.scores["quantization"])

        boxes, scores, masks = decode_yolo_boxes(
            p=x,
            with_masks=self.parameters.common.with_masks,
            nc=len(self.parameters.labels)
        )

        boxes, classes, scores, masks = nms(
            boxes=boxes,
            scores=scores,
            masks=masks,
            iou_threshold=self.parameters.iou_threshold,
            score_threshold=self.parameters.score_threshold,
            max_detections=self.parameters.max_detections,
            class_agnostic=self.parameters.agnostic_nms,
            nms_type=self.parameters.nms
        )

        # Normalize bounding boxes if not already.
        if boxes.shape[0] > 0:
            normalized_conf = np.mean((boxes >= 0) & (boxes <= 1))
            if not normalized_conf >= 0.80:
                boxes[..., [0, 2]] /= w
                boxes[..., [1, 3]] /= h

        # Decode Masks.
        if masks is not None:
            protos = output[self.outputs.masks["index"]]
            if protos.dtype == np.float16:
                protos = protos.astype(np.float32)
            if (self.outputs.masks["quantization"] is not None and
                    protos.dtype != np.float32):
                protos = dequantize(
                    protos, *self.outputs.masks["quantization"])
            masks = decode_yolo_masks(masks, protos=protos)

            # Mask postprocessing: resize + crop.
            if masks.shape[0] > 0:
                masks = (masks > 0).astype(np.uint8)
                masks = [resize(mask, size=(w, h),
                                backend=self.parameters.common.backend)
                         for mask in masks]
                masks = np.stack(masks, axis=0)
                masks = crop_masks(masks, boxes)

        return boxes, classes, scores, masks

    def process_yolox(self, outputs: List[np.ndarray]) -> DetOutput:
        """
        YOLOx output decoding and postprocessing.

        Parameters
        ----------
        outputs: List[np.ndarray]
            YOLOx raw output to postprocess into
            bounding boxes, classes, scores after NMS. This
            typically has the shape (1, 8400, 85).

        Returns
        -------
        Tuple[np.ndarray, np.ndarray, np.ndarray]
            np.ndarray
                The prediction bounding boxes.. [[box1], [box2], ...].
            np.ndarray
                The prediction labels.. [cl1, cl2, ...].
            np.ndarray
                The prediction confidence scores.. [score, score, ...]
                normalized between 0 and 1.
        """

        output = outputs[0] if len(outputs) == 1 else outputs
        output = output.numpy() if not isinstance(
            output, (np.ndarray, list)) else output

        height, width = get_shape(self.shape)
        if (self.outputs.scores["quantization"] is not None and
                output.dtype != np.float32):
            output = dequantize(output, *self.outputs.scores["quantization"])

        boxes, scores = decode_yolox_boxes(
            p=output,
            shape=(height, width)
        )
        boxes = xcycwh2xyxy(boxes=boxes)

        # Typical: nms_thr=0.45, score_thr=0.1
        dets = multiclass_nms(
            boxes=boxes,
            scores=scores,
            iou_threshold=self.parameters.iou_threshold,
            score_threshold=self.parameters.score_threshold,
            max_detections=self.parameters.max_detections,
            class_agnostic=self.parameters.agnostic_nms,
            nms_type=self.parameters.nms
        )
        if dets is None:
            return np.array([]), np.array([]), np.array([])

        boxes = dets[:, :4]
        scores = dets[:, 4]
        classes = dets[:, 5]

        # Normalize the bounding boxes.
        boxes /= np.array([width, height, width, height])
        return boxes, classes, scores

    def get_input_type(self) -> str:
        """Abstract Method"""
        pass

    def get_input_shape(self) -> np.ndarray:
        """Abstract Method"""
        pass

from __future__ import annotations

from typing import TYPE_CHECKING, Tuple

import numpy as np

from edgefirst.validator.evaluators import Evaluator
from edgefirst.validator.datasets import MultitaskInstance
from edgefirst.validator.evaluators import (YOLOValidator, EdgeFirstValidator,
                                            SegmentationValidator)
from edgefirst.validator.metrics import MultitaskMetrics, MultitaskPlots

if TYPE_CHECKING:
    from edgefirst.validator.evaluators import CombinedParameters
    from edgefirst.validator.datasets import Dataset
    from edgefirst.validator.runners import Runner


class MultitaskValidator(Evaluator):
    """
    This class handles validation of Vision models that outputs
    bounding boxes and segmentation masks on an image.
    This class is only intended for EdgeFirst validation. The multitask
    validation from Ultralytics is implemented under
    `YOLOSegmentationValidator`.

    Parameters
    ----------
    parameters: CombinedParameters
        This is a container for the model, dataset, and validation parameters
        set from the command line.
    runner: Runner
        A type of model runner object responsible for running the model
        for inference provided with an input image to produce bounding boxes.
    dataset: Dataset
        A type of dataset object responsible for reading different types
        of datasets such as Darknet, TFRecords, or EdgeFirst Datasets.
    """

    def __init__(
        self,
        parameters: CombinedParameters,
        runner: Runner = None,
        dataset: Dataset = None,
    ):
        super(MultitaskValidator, self).__init__(
            parameters=parameters, runner=runner, dataset=dataset)

        if self.parameters.validation.method in ["ultralytics", "yolov7"]:
            self.detection_evaluator = YOLOValidator(
                parameters=parameters,
                runner=None,
                dataset=dataset
            )
        else:
            self.detection_evaluator = EdgeFirstValidator(
                parameters=parameters,
                runner=None,
                dataset=dataset
            )

        self.segmentation_evaluator = SegmentationValidator(
            parameters=parameters,
            runner=None,
            dataset=dataset
        )
        self.parameters.model.common.semantic = True

        self.metrics = MultitaskMetrics(
            detection_metrics=self.detection_evaluator.metrics.metrics,
            segmentation_metrics=self.segmentation_evaluator.metrics.metrics
        )
        self.plots = MultitaskPlots(
            detection_plots=self.detection_evaluator.metrics.plots,
            segmentation_plots=self.segmentation_evaluator.metrics.plots
        )

    def instance_collector(self):
        """
        Collects the Multitask instances from the ground truth and runs
        model inference on a single image to collect the instance for
        the model predictions.

        Yields
        ------
        dict
            This yields one image instance from the ground truth
            and model predictions for multitask with keys
            "gt_instance", "dt_instance".
        """

        gt_instance: MultitaskInstance
        for gt_instance in self.dataset:
            detections = self.runner.run_single_instance(
                image=gt_instance.image
            )
            self.detection_evaluator.filter_gt(gt_instance)

            if detections is None:
                yield {
                    "gt_instance": gt_instance,
                    "dt_instance": None,
                }

            dt_instance = MultitaskInstance(gt_instance.image_path)
            boxes, labels, scores, mask = detections
            dt_instance.height = gt_instance.height
            dt_instance.width = gt_instance.width
            dt_instance.boxes = boxes
            dt_instance.labels = labels
            dt_instance.scores = scores
            dt_instance.mask = self.segmentation_evaluator.calibrate_mask(
                mask, dt_labels=dt_instance.labels)
            self.detection_evaluator.filter_dt(dt_instance)

            yield {
                "gt_instance": gt_instance,
                "dt_instance": dt_instance,
            }

    def single_evaluation(
        self,
        instance: dict,
        epoch: int = 0,
        save_image: bool = False
    ):
        """
        Run model evaluation on a single image/sample for both
        detection and segmentation.

        Parameters
        ----------
        instance: dict
            This contains the ground truth
            and model predictions for multitask with keys
            "gt_instance", "dt_instance".
        epoch: int
            This is the training epoch number. This
            parameter is internal for ModelPack usage.
            Standalone validation does not use this parameter.
        save_image: bool
            If set to True, this will save the image
            with drawn bounding box results.
        """
        self.detection_evaluator.single_evaluation(
            instance=instance,
            epoch=epoch,
            save_image=False
        )
        self.segmentation_evaluator.single_evaluation(
            instance=instance,
            epoch=epoch,
            save_image=False
        )

        super().single_evaluation(instance=instance,
                                  epoch=epoch,
                                  save_image=save_image)

    def visualize(
        self,
        gt_instance: MultitaskInstance,
        dt_instance: MultitaskInstance,
        epoch: int = 0
    ):
        """
        Visualize the multi-task outputs for detection
        and segmentation on the image.

        Parameters
        ----------
        gt_instance: DetectionInstance
            This is the ground truth instance which contains the
            masks, bounding boxes and labels to draw.
        dt_instance: DetectionInstance
            This is the model detection instance which contains the
            masks, bounding boxes, labels, and confidence scores to draw.
        epoch: int
            This is the training epoch number. This
            parameter is internal for ModelPack usage.
            Standalone validation does not use this parameter.

        """
        # Separate results for the ground truth and detection.
        dt_instance.visual_image = gt_instance.visual_image.copy()

        # Draw ground truth on the ground truth image.
        image = self.detection_evaluator.drawer.draw_2d_gt_boxes(
            image=gt_instance.visual_image,
            gt_instance=gt_instance
        )
        gt_instance.visual_image = np.asarray(image)

        # Draw detections on the detection image.
        image = self.detection_evaluator.drawer.draw_2d_dt_boxes(
            image=dt_instance.visual_image,
            gt_instance=gt_instance,
            dt_instance=dt_instance,
            matcher=self.detection_evaluator.matcher,
            validation_iou=self.parameters.validation.iou_threshold,
            method=self.parameters.validation.method
        )
        dt_instance.visual_image = np.asarray(image)

        # Draw segmentation results on the image.
        self.segmentation_evaluator.visualize(
            gt_instance=gt_instance,
            dt_instance=dt_instance,
            epoch=epoch
        )

    def end(
        self,
        epoch: int = 0,
        reset: bool = True
    ) -> Tuple[MultitaskMetrics, MultitaskPlots]:
        """
        Computes the final metrics for detection and segmentation and
        generates the validation plots to save the results in disk or
        publishes to Tensorboard.

        Parameters
        ----------
        epoch: int
            This is the training epoch number. This
            parameter is internal for ModelPack usage.
            Standalone validation does not use this parameter.
        reset: bool
            This is an optional parameter that controls the reset state.
            By default, it will reset at the end of validation to erase
            the data in the containers.

        Returns
        -------
        metrics: MultitaskMetrics
            This is a container for the detection and segmentation metrics.
        plots: MultitaskPlots
            This is a container for the validation data for plotting.
        """
        if hasattr(self.runner, "stop"):
            self.runner.stop()

        if self.runner:
            timings = self.runner.timer.to_dict()

        self.metrics.timings = timings
        detection_metrics, detection_plots = self.detection_evaluator.end(
            epoch=epoch, reset=reset, publish=False)
        segmentation_metrics, segmentation_plots = self.segmentation_evaluator.end(
            epoch=epoch, reset=reset, publish=False)

        self.metrics.detection_metrics = detection_metrics
        self.metrics.segmentation_metrics = segmentation_metrics
        self.plots.detection_plots = detection_plots
        self.plots.segmentation_plots = segmentation_plots

        if self.tensorboard_writer:
            self.tensorboard_writer.publish_metrics(
                metrics=self.metrics,
                parameters=self.parameters,
                step=epoch,
            )
        else:
            table = self.console_writer(metrics=self.metrics,
                                        parameters=self.parameters)

            if self.parameters.validation.visualize:
                self.console_writer.save_metrics(table)

        return self.metrics, self.plots

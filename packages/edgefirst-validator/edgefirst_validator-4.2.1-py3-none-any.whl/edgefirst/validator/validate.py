from __future__ import annotations

import os
import ast
import zipfile
import datetime
import traceback
from typing import TYPE_CHECKING, Union, List, Tuple

import yaml
from edgefirst_client import Client

from edgefirst.validator.datasets import instantiate_dataset
from edgefirst.validator.datasets.utils.fetch import (classify_dataset,
                                                      download_file)
from edgefirst.validator.datasets.utils.readers import (read_labels_file,
                                                        read_yaml_file)
from edgefirst.validator.publishers.utils.logger import (logger,
                                                         set_symbol_condition)
from edgefirst.validator.runners import (TFliteRunner, ONNXRunner, KerasRunner,
                                         TensorRTRunner, OfflineRunner,
                                         DeepViewRTRunner, KinaraRunner)
from edgefirst.validator.evaluators import (CombinedParameters, CommonParameters,
                                            ModelParameters, DatasetParameters,
                                            ValidationParameters, TimerContext)
from edgefirst.validator.evaluators import (YOLOValidator, EdgeFirstValidator,
                                            YOLOSegmentationValidator,
                                            SegmentationValidator,
                                            MultitaskValidator,
                                            StudioProgress)
from edgefirst.validator.publishers import StudioPublisher
from edgefirst.validator.datasets import StudioCache

if TYPE_CHECKING:
    from edgefirst.validator.runners import Runner
    from edgefirst.validator.datasets import Dataset
    from edgefirst.validator.evaluators import Evaluator


def build_parameters(args) -> CombinedParameters:
    """
    Store command line arguments inside the `Parameters` object.

    Parameters
    ----------
    args: argsparse.NameSpace
        The command line arguments.

    Returns
    -------
    CombinedParameters
        This object is a container for both the model
        and validation parameters set from the command line.
    """
    # Time of validation
    today = datetime.datetime.now().strftime(
        '%Y-%m-%d--%H:%M:%S').replace(":", "_")
    tensorboard, visualize, json_out = None, None, None
    if args.visualize:
        visualize = os.path.join(
            args.visualize,
            f"{os.path.basename(os.path.normpath(args.model))}_{today}")
    elif args.tensorboard:
        tensorboard = os.path.join(
            args.tensorboard,
            f"{os.path.basename(os.path.normpath(args.model))}_{today}"
        )

    json_out = args.json_out
    if args.session_id is not None:
        if json_out is None:
            json_out = "apex_charts"

    if json_out:
        json_out = os.path.join(
            json_out,
            f"{os.path.basename(os.path.normpath(args.model))}_{today}"
        )

    validation_parameters = ValidationParameters(
        method=args.method,
        iou_threshold=args.validation_iou,
        score_threshold=args.validation_score,
        metric=args.metric,
        matching_leniency=args.matching_leniency,
        clamp_boxes=args.clamp_boxes,
        ignore_boxes=args.ignore_boxes,
        display=args.display,
        visualize=visualize,
        tensorboard=tensorboard,
        json_out=json_out,
        csv_out=args.csv,
        include_background=args.include_background
    )

    common_parameters = CommonParameters(
        norm=args.norm,
        preprocessing=args.preprocessing,
        backend=args.backend
    )
    common_parameters.check_backend_availability()

    model_parameters = ModelParameters(
        common_parameters=common_parameters,
        model_path=args.model,
        iou_threshold=args.nms_iou_threshold,
        score_threshold=args.nms_score_threshold,
        max_detections=args.max_detections,
        engine=args.engine,
        nms=args.nms,
        box_format=args.box_format,
        warmup=args.warmup,
        labels_path=args.model_labels,
        label_offset=args.label_offset,
        agnostic_nms=not args.class_nms
    )
    model_parameters.check_nms_availability()

    dataset_parameters = DatasetParameters(
        common_parameters=common_parameters,
        dataset_path=args.dataset,
        show_missing_annotations=args.show_missing_annotations,
        normalized=args.absolute_annotations,
        box_format=args.annotation_format,
        labels_path=args.dataset_labels,
        label_offset=args.gt_label_offset,
    )
    dataset_parameters.silent = validation_parameters.silent
    dataset_parameters.visualize = (validation_parameters.visualize or
                                    validation_parameters.tensorboard)

    parameters = CombinedParameters(
        model_parameters=model_parameters,
        dataset_parameters=dataset_parameters,
        validation_parameters=validation_parameters
    )

    if (model_parameters.nms in ["hal", "numpy", "torch"] and
            not model_parameters.agnostic_nms):
        logger(
            "Class-based NMS is currently not supported for the {} NMS.".format(
                model_parameters.nms), code="INFO"
        )
    return parameters


def build_dataset(
    args,
    parameters: DatasetParameters,
    timer: TimerContext,
    studio_cache: StudioCache,
) -> Dataset:
    """
    Instantiate the Dataset Reader.

    Parameters
    ----------
    args: argsparse.NameSpace
        The command line arguments.
    parameters: DatasetParameters
        Contains the dataset parameters set from the command line.
    timer: TimerContext
        A timer object for handling validation timings in
        the dataset input preprocessing.
    studio_cache: StudioCache
        The object used for downloading and caching the dataset.

    Returns
    -------
    Dataset
        This can be any dataset reader such as a DarkNetDataset,
        EdgeFirstDatabase, etc. depending on the dataset format that
        was specified.
    """

    if args.session_id is not None:
        # Avoid the default dataset path for studio validation.
        if args.dataset == "samples/coco128.yaml":
            args.dataset = "dataset"
            parameters.dataset_path = args.dataset

        if parameters.labels_path and os.path.exists(parameters.labels_path):
            parameters.labels = read_labels_file(parameters.labels_path)

        # Download the dataset if it doesn't exist.
        if not (os.path.exists(args.dataset) and os.listdir(args.dataset)):
            logger("The dataset does not exist. " +
                   f"Attempting to download the dataset to '{args.dataset}'",
                   code="INFO")
            studio_cache.download(args.dataset)
        else:
            studio_cache.complete_stage(
                stage=studio_cache.stages[0][0],
                message=studio_cache.stages[0][1]
            )
            studio_cache.complete_stage(
                stage=studio_cache.stages[1][0],
                message=studio_cache.stages[1][1]
            )

    # Use the dataset cache if specified and it exists.
    if args.cache is not None:
        parameters.cache = True
        if os.path.exists(args.cache):
            parameters.dataset_path = args.cache
            studio_cache.complete_stage(
                stage=studio_cache.stages[2][0],
                message=studio_cache.stages[2][1]
            )

    # Determine the dataset type.
    info_dataset = classify_dataset(
        source=parameters.dataset_path,
        labels_path=parameters.labels_path
    )

    # Build the dataset class depending on the type.
    return instantiate_dataset(
        info_dataset=info_dataset,
        parameters=parameters,
        timer=timer
    )


def build_runner(args, parameters: ModelParameters,
                 timer: TimerContext) -> Runner:
    """
    Instantiate the model runners.

    Parameters
    ----------
    args: argsparse.NameSpace
        The command line arguments.
    parameters: ModelParameters
        Contains the model parameters set from the command line.
    timer: TimerContext
        A timer object for handling validation timings in the model.

    Returns
    -------
    Runner
        This can be any model runner depending on the model passed
        such as ONNX, TFLite, Keras, RTM, etc.

    Raises
    ------
    NotImplementedError
        Certain runner implementations are not yet implemented.
    """
    if (not os.path.exists(parameters.model_path) and
            parameters.model_path == "yolov5s.onnx"):
        download_file(
            url="https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.onnx",
            download_path=os.path.join(os.getcwd(), "yolov5s.onnx")
        )

    model_metadata = get_model_metadata(args)
    # Validate with the model metadata parameters.
    # By default in the command line override is set to True to use
    # the command line parameters. Otherwise in EdgeFirst Studio, override
    # is set to False to use model meta parameters.
    if not args.override and model_metadata is not None:
        parameters.score_threshold = model_metadata\
            .get("validation", {})\
            .get("score",
                 parameters.score_threshold)
        parameters.iou_threshold = model_metadata\
            .get("validation", {})\
            .get("iou", parameters.iou_threshold)
        parameters.common.norm = model_metadata\
            .get("validation", {})\
            .get("normalization", parameters.common.norm)
        parameters.common.preprocessing = model_metadata\
            .get("validation", {})\
            .get("preprocessing",
                 parameters.common.preprocessing)

    # KERAS
    if os.path.splitext(parameters.model_path)[1].lower() in [".h5", ".keras"]:
        runner = KerasRunner(parameters.model_path,
                             parameters=parameters,
                             metadata=model_metadata,
                             timer=timer)
    # TFLITE
    elif os.path.splitext(parameters.model_path)[1].lower() == ".tflite":
        runner = TFliteRunner(parameters.model_path,
                              parameters=parameters,
                              metadata=model_metadata,
                              timer=timer)
    # ONNX
    elif os.path.splitext(parameters.model_path)[1].lower() == ".onnx":
        runner = ONNXRunner(parameters.model_path,
                            parameters=parameters,
                            metadata=model_metadata,
                            timer=timer)
    # TENSORRT
    elif os.path.splitext(parameters.model_path)[1].lower() in [".engine", ".trt"]:
        runner = TensorRTRunner(parameters.model_path,
                                parameters=parameters,
                                metadata=model_metadata,
                                timer=timer)
    # KINARA
    elif os.path.splitext(parameters.model_path)[1].lower() == ".dvm":
        runner = KinaraRunner(
            parameters.model_path,
            parameters=parameters,
            metadata=model_metadata,
            timer=timer
        )
    # HAILO
    elif os.path.splitext(parameters.model_path)[1].lower() == ".hef":
        raise NotImplementedError(
            "Running Hailo models is not implemented.")
    # DEEPVIEWRT EVALUATION
    elif os.path.splitext(parameters.model_path)[1].lower() == ".rtm":
        runner = DeepViewRTRunner(
            model=parameters.model_path,
            parameters=parameters,
            metadata=model_metadata,
            timer=timer
        )
    # OFFLINE (TEXT FILES) or SAVED MODEL Directory
    elif os.path.splitext(parameters.model_path)[1].lower() == "":
        runner = find_keras_pb_model(parameters=parameters,
                                     metadata=model_metadata,
                                     timer=timer)

        if runner is None:
            logger("Model extension does not exist, running offline validation.",
                   code='INFO')

            runner = OfflineRunner(
                annotation_source=parameters.model_path,
                parameters=parameters,
                timer=timer
            )
    else:
        raise NotImplementedError(
            "Running the model '{}' is currently not supported".format(
                parameters.model_path)
        )
    return runner


def build_evaluator(
    args,
    parameters: CombinedParameters,
    client: Client,
    stages: List[Tuple[str, str]]
) -> Evaluator:
    """
    Intantiate the evaluator object depending on the task.

    Parameters
    ----------
    args: argsparse.NameSpace
        The command line arguments.
    parameters: CombinedParameters
        This object is a container for both model, dataset, and validation
        parameters set from the command line.
    client: Client
        The EdgeFirst Client object.
    stages: List[Tuple[str, str]]
        This contains the stages that tracks each progress in Studio.
        A stage contains ("stage identifier", "stage description").

    Returns
    -------
    Evaluator
        This can be any evaluator object depending on the task such
        as segmentation, detection, multitask, or pose.

    Raises
    ------
    ValueError
        Dataset labels were not found.
    NotImplementedError
        Certain validation types are not yet implemented.
    """
    timer = TimerContext()
    studio_cache = StudioCache(
        parameters=parameters.dataset,
        stages=stages,
        client=client,
        session_id=args.session_id,
    )

    dataset = build_dataset(
        args, parameters=parameters.dataset, timer=timer,
        studio_cache=studio_cache,
    )

    if parameters.dataset.labels is None or len(
            parameters.dataset.labels) == 0:
        raise ValueError(
            "The unique set of string labels from the dataset was not found. " +
            "Try setting --dataset-labels=path/to/labels.txt")

    # Read labels.txt or assign the dataset labels as the model labels as a fallback.
    # During validation, all model indices will be translated to the dataset indices
    # for a 1-to-1 match.
    if parameters.model.labels is None or len(parameters.model.labels) == 0:
        parameters.model.labels = get_model_labels(args, parameters.dataset)

    # Builds the runner and assigns conditions for with_masks or with_boxes.
    runner = build_runner(args, parameters=parameters.model, timer=timer)

    # Cache the dataset if it doesn't exist.
    # This block is placed after the building the runner object to initialize
    # with_masks and with_boxes conditions needed for iterating the dataset.
    if args.cache is not None and not os.path.exists(args.cache):
        logger("The dataset cache does not exist. " +
               f"Attempting to cache existing dataset to {args.cache}",
               code="INFO")
        dataset = instantiate_dataset(
            info_dataset=dataset.info_dataset,
            parameters=parameters.dataset,
            timer=timer
        )
        dataset = studio_cache.cache(dataset, args.cache)
        parameters.dataset.dataset_path = args.cache

    dataset.verify_dataset()

    # If the model labels has background, but the dataset does not,
    # include background in the dataset labels with a +1 offset to label
    # indices.
    if ("background" in parameters.model.labels and
            "background" not in parameters.dataset.labels):
        parameters.dataset.labels = ['background'] + parameters.dataset.labels
        parameters.dataset.label_offset = 1

    # If the labels in the dataset and the model do not match.
    # However consider possibility of the background class inside the dataset.
    if abs(len(parameters.dataset.labels) - len(parameters.model.labels)) > 1:
        logger(
            "The model contains {} labels and the dataset contains {} labels.".format(
                len(parameters.model.labels),
                len(parameters.dataset.labels)
            ),
            code="WARNING")

        dataset_labels = parameters.dataset.labels
        model_labels = parameters.model.labels
        if len(dataset_labels) < len(model_labels):
            offset = len(model_labels) - len(dataset_labels)
            parameters.dataset.labels += ["unknown"] * offset
        else:
            offset = len(dataset_labels) - len(model_labels)
            parameters.model.labels += ["unknown"] * offset

    """
    Instantiate evaluators
    """
    # Multitask Validation
    if parameters.model.common.with_boxes and parameters.model.common.with_masks:
        if (not parameters.model.common.semantic and
                parameters.validation.method in ["ultralytics", "yolov7"]):
            # Ultralytics segmentation models are always multitask models.
            evaluator = YOLOSegmentationValidator(
                parameters=parameters,
                runner=runner,
                dataset=dataset
            )
        else:
            logger("Detected semantic segmentation model. " +
                   "Deploying EdgeFirst validation.",
                   code="INFO")
            evaluator = MultitaskValidator(
                parameters=parameters,
                runner=runner,
                dataset=dataset
            )
    # Segmentation Validation
    elif parameters.model.common.with_masks:
        logger("Detected semantic segmentation model. " +
               "Deploying EdgeFirst validation.",
               code="INFO")
        # Semantic Segmentation models from ModelPack are validated using
        # EdgeFirst
        parameters.validation.method = "edgefirst"
        evaluator = SegmentationValidator(
            parameters=parameters,
            runner=runner,
            dataset=dataset
        )
    # Detection Validation
    elif parameters.model.common.with_boxes:
        if parameters.validation.method in ["ultralytics", "yolov7"]:
            evaluator = YOLOValidator(
                parameters=parameters,
                runner=runner,
                dataset=dataset
            )
        else:
            evaluator = EdgeFirstValidator(
                parameters=parameters,
                runner=runner,
                dataset=dataset
            )
    else:
        raise RuntimeError(
            "Both values for `with_boxes` and `with_masks` were set to False.")

    return evaluator


def find_keras_pb_model(
    parameters: ModelParameters,
    metadata: dict,
    timer: TimerContext
) -> Union[KerasRunner, None]:
    """
    Instantiate Keras runners based on pb model extension.

    Parameters
    ----------
    parameters: Parameters
        These are the model parameters loaded by the command line.
    metadata: dict
        The model metadata which contains information for decoding
        the model outputs.
    timer: TimerContext
        A timer object handling validation timings in the model.

    Returns
    -------
    Union[KerasRunner, None]
        If 'keras_metadata.pb' or 'saved_model.pb' files exists, then
        the KerasRunner is instantiated. This is the runner object for
        deploying Keras models for inference. Otherwise, None is returned.
    """
    runner = None
    for root, _, files in os.walk(parameters.model_path):
        for file in files:
            if (os.path.basename(file) == "keras_metadata.pb" or
                    os.path.basename(file) == "saved_model.pb"):
                runner = KerasRunner(
                    model=root,
                    parameters=parameters,
                    metadata=metadata,
                    timer=timer
                )
                break
    return runner


def get_model_labels(args, parameters: DatasetParameters) -> list:
    """
    Fetch the labels associated to the model.

    Parameters
    ----------
    args: argsparse.NameSpace
        The command line arguments.
    parameters: DatasetParameters
        The dataset parameters set from the command line.

    Returns
    -------
    list
        The list of model labels.
    """
    model_labels = parameters.labels

    arg_labels, embedded_labels = [], []
    if args.model_labels and os.path.exists(args.model_labels):
        arg_labels = read_labels_file(args.model_labels)
        model_labels = arg_labels

    if args.model.endswith('.tflite'):
        if zipfile.is_zipfile(args.model):
            with zipfile.ZipFile(args.model, 'r') as zip_ref:
                # Find the first .txt file inside the ZIP.
                txt_files = [name for name in zip_ref.namelist()
                             if name.lower().endswith('.txt')]
                if txt_files:
                    # Pick the first .txt file (or handle multiple if needed).
                    with zip_ref.open(txt_files[0]) as file:
                        content = file.read().decode('utf-8').strip()
                        try:
                            model_metadata = ast.literal_eval(content)
                            names = model_metadata.get("names", {})
                            embedded_labels = [name for name in names.values()]
                        except (ValueError, SyntaxError):
                            embedded_labels = [line
                                               for line in content.splitlines()
                                               if line not in ["\n", "", "\t"]]
                        model_labels = embedded_labels

    if len(arg_labels) and len(embedded_labels):
        if arg_labels != embedded_labels:
            logger("The contents of the specified --model-labels does not match " +
                   "the labels embedded in the model. Falling back to the " +
                   "labels embedded in the model", code="WARNING")

    if not (len(arg_labels) or len(embedded_labels)):
        logger("Model labels was not specified. " +
               "Falling back to use the dataset labels for the model.",
               code="WARNING")
    return model_labels


def get_model_metadata(args) -> Union[dict, None]:
    """
    Returns the model metadata for decoding the outputs.

    Parameters
    ----------
    args: argsparse.NameSpace
        The command line arguments.

    Returns
    -------
    Union[dict, None]
        The model metadata if it exists. Otherwise None is returned.
    """
    if args.config is not None:
        return read_yaml_file(args.config)
    if zipfile.is_zipfile(args.model):
        with zipfile.ZipFile(args.model) as zip_ref:
            if "edgefirst.yaml" in zip_ref.namelist():
                file = "edgefirst.yaml"
            elif "config.yaml" in zip_ref.namelist():
                file = "config.yaml"
            else:
                return None
            with zip_ref.open(file) as f:
                yaml_text = f.read().decode("utf-8")
                metadata = yaml.safe_load(yaml_text)
                return metadata
    return None


def download_model_artifacts(args, client: Client):
    """
    Download model artifacts in EdgeFirst Studio.

    Parameters
    ----------
    args: argsparse.NameSpace
        The command line arguments.
    client: Client
        The EdgeFirst Studio client object to
        communicate with EdgeFirst Studio.
    """
    session = client.validation_session(session_id=args.session_id)

    train_session_id = session.training_session_id
    model = session.params["model"]

    logger(f"Downloading model artifacts from train session ID " +
           f"'t-{train_session_id.value:x}'.", code="INFO")

    # Do not auto-download the model, in case offline validation is specified.
    if not os.path.exists(args.model):
        model = str(model)
        if "String" in model:
            model = model.removeprefix("String(").removesuffix(")")

        try:
            client.download_artifact(
                training_session_id=train_session_id,
                modelname=model,
                filename=model
            )
        except RuntimeError as e:
            if "Status(404" in str(e):
                raise FileNotFoundError(
                    f"The artifact '{model}' does not exist.")
            raise e
        args.model = os.path.join(os.path.dirname(args.model), model)

    if args.model_labels is None:
        args.model_labels = "labels.txt"

    if args.config is None:
        args.config = "edgefirst.yaml"

    try:
        client.download_artifact(
            training_session_id=train_session_id,
            modelname=args.model_labels,
            filename=args.model_labels
        )
    except RuntimeError as e:
        if "Status(404" in str(e):
            raise FileNotFoundError(
                "The artifact 'labels.txt' does not exist.")
        raise e

    try:
        client.download_artifact(
            training_session_id=train_session_id,
            modelname=args.config,
            filename=args.config
        )
    except RuntimeError as e:
        if "Status(404" in str(e):
            raise FileNotFoundError(
                "The artifact 'edgefirst.yaml' does not exist.")
        raise e


def update_parameters(args, client: Client):
    """
    Updates the parameters specified by EdgeFirst Studio.

    Parameters
    ----------
    args: argsparse.NameSpace
        The command line arguments.
    client: Client
        The EdgeFirst Client object.
    """
    session = client.validation_session(args.session_id)

    args.method = session.params.get("method", args.method)
    args.override = "override" in session.params.keys()
    args.nms_score_threshold = session.params.get("nms_score_threshold",
                                                  args.nms_score_threshold)
    args.nms_iou_threshold = session.params.get("nms_iou_threshold",
                                                args.nms_iou_threshold)


def initialize_studio_client(args) -> Union[Client, None]:
    """
    Initialize the EdgeFirst Client if the validation session ID is set.
    Downloads the model artifacts if it doesn't exist.

    Parameters
    ----------
    args: argsparse.NameSpace
        The command line arguments.

    Returns
    -------
    Union[Client, None]
        The EdgeFirst client object is a bridge of communication between
        EdgeFirst Studio and the applications. Otherwise None is
        returned if the validation session ID is not specified.
    """
    client = None
    if args.session_id is not None:
        if args.session_id.isdigit():
            args.session_id = int(args.session_id)
        logger(f"Detected EdgeFirst Studio validation ID: '{args.session_id}'.",
               code="INFO")

        try:
            client = Client(
                token=args.token,
                username=args.username,
                password=args.password,
                server=args.server
            )
        except RuntimeError as e:
            if "MaxRetries" in str(e):
                raise ValueError(
                    f"Got an invalid server: {args.server}. " +
                    "Check that the right server is set.")
            raise e
    return client


def validate(args):
    """
    Instantiates the runners and readers to deploy the model for validation.

    Parameters
    ----------
    args: argsparse.NameSpace
        The command line arguments set.
    """
    set_symbol_condition(args.exclude_symbols)

    client = initialize_studio_client(args)
    studio_publisher = None
    evaluator = None

    # Progress stages are defined in the order below.
    # If the order is to change, update the stages defined in StudioCache.
    stages = [
        ("fetch_img", "Downloading Images"),
        ("fetch_as", "Downloading Annotations"),
        ("validate", "Running Validation"),
    ]
    if args.cache is not None:
        stages.insert(2, ("cache", "Caching Dataset"))

    if client is not None:
        studio_publisher = StudioPublisher(
            json_path=args.json_out,
            session_id=args.session_id,
            client=client
        )

    try:
        if studio_publisher is not None:
            session = client.validation_session(session_id=args.session_id)
            client.set_stages(session.task.id, stages)

            download_model_artifacts(args, client=client)
            # Update parameters set from the validation session in studio.
            update_parameters(args=args, client=client)

            parameters = build_parameters(args)
            studio_publisher.json_path = parameters.validation.json_out
        else:
            parameters = build_parameters(args)
        evaluator = build_evaluator(args, parameters=parameters,
                                    client=client, stages=stages)
    except Exception as e:
        if studio_publisher is not None:
            studio_publisher.update_stage(
                stage="validate",
                status="error",
                message=str(e),
                percentage=0
            )
        if evaluator is not None:
            evaluator.stop()
        error = traceback.format_exc()
        print(error)
        raise e

    if args.session_id is not None:
        studio_progress = StudioProgress(
            evaluator=evaluator,
            studio_publisher=studio_publisher,
            stage=stages[-1][0]
        )
        try:
            studio_progress.group_evaluation()
        except Exception as e:
            evaluator.stop()
            raise e
    else:
        try:
            evaluator.group_evaluation()
        except Exception as e:
            evaluator.stop()
            raise e

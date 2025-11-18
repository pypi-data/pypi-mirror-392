"""
This module contains functions for transforming dataset artifacts.
"""

from __future__ import annotations

import math
import numbers
from io import BytesIO
from typing import TYPE_CHECKING, Union, Tuple, Any, List, Callable

import numpy as np
from PIL import Image, ImageDraw, ExifTags

# Transform label synonyms to a common representation.
COCO_LABEL_SYNC = {
    "motorbike": "motorcycle",
    "aeroplane": "airplane",
    "sofa": "couch",
    "pottedplant": "potted plant",
    "diningtable": "dining table",
    "tvmonitor": "tv"
}

try:
    import edgefirst_python  # type: ignore
    CONVERTER = edgefirst_python.ImageConverter()
except ImportError:
    CONVERTER = None

if TYPE_CHECKING:
    from edgefirst_python import TensorImage  # type: ignore

# Functions for Sensor Transformations


def bgr2rgb(image: np.ndarray) -> np.ndarray:
    """
    Converts BGR image to RGB image.

    Parameters
    ----------
    image: (height, width, 3) np.ndarray
        The BGR image NumPy array.

    Returns
    -------
    np.ndarray
        The RGB image NumPy array.
    """
    return image[:, :, ::-1]


def rgb2bgr(image: np.ndarray) -> np.ndarray:
    """
    Converts RGB image to BGR image.

    Parameters
    ----------
    image: (height, width, 3) np.ndarray
        The RGB image NumPy array.

    Returns
    -------
    np.ndarray
        The BGR image NumPy array.
    """
    return bgr2rgb(image)


def rgb2yuyv(image: np.ndarray, backend: str = "hal") -> np.ndarray:
    """
    Convert an RGB image to YUYV format using the EdgeFirst Tensor API.

    Parameters
    ----------
    image: np.ndarray
        The 3-channel RGB image NumPy array.
    backend: str
        The backend library to use for this conversion.

    Returns
    -------
    np.ndarray
        The 2-channel YUYV image array.
    """

    if backend == "hal":
        try:
            import edgefirst_python  # type: ignore
        except ImportError:
            raise ImportError(
                "EdgeFirst HAL is needed to perform RGB to YUYV conversion.")

        height, width, _ = image.shape
        src = edgefirst_python.TensorImage(
            width, height, fourcc=edgefirst_python.FourCC.RGB)
        src.copy_from_numpy(image)

        dst = edgefirst_python.TensorImage(
            width, height, fourcc=edgefirst_python.FourCC.YUYV)
        CONVERTER.convert(src, dst)

        im = np.zeros((dst.height, dst.width, 2), dtype=np.uint8)
        dst.normalize_to_numpy(im)
        return im
    else:
        try:
            import cv2
        except ImportError:
            raise ImportError(
                "OpenCV is needed to perform RGB to YUYV conversion.")
        return cv2.cvtColor(image, cv2.COLOR_RGB2YUV_YUY2)


def yuyv2rgb(image: np.ndarray, backend: str = "hal") -> np.ndarray:
    """
    Convert a YUYV image to RGB format using the EdgeFirst Tensor API.

    Parameters
    ----------
    image: np.ndarray
        The input 2-channel YUYV image.
    backend: str
        The backend library to use for this conversion.

    Returns
    -------
    np.ndarray
        The output 3-channel RGB image.
    """

    if backend == "hal":
        try:
            import edgefirst_python  # type: ignore
        except ImportError:
            raise ImportError(
                "EdgeFirst HAL is needed to perform YUYV to RGB conversion.")

        height, width, _ = image.shape
        src = edgefirst_python.TensorImage(
            width, height, fourcc=edgefirst_python.FourCC.YUYV)
        src.copy_from_numpy(image)

        dst = edgefirst_python.TensorImage(
            width, height, fourcc=edgefirst_python.FourCC.RGB)
        CONVERTER.convert(src, dst)

        im = np.zeros((dst.height, dst.width, 3), dtype=np.uint8)
        dst.normalize_to_numpy(im)
        return im
    else:
        try:
            import cv2
        except ImportError:
            raise ImportError(
                "OpenCV is needed to perform YUYV to RGB conversion.")
        return cv2.cvtColor(image, cv2.COLOR_YUV2RGB_YUY2)


def rgb2rgba(image: np.ndarray, backend: str = "hal") -> np.ndarray:
    """
    Convert a 3-channel RGB image to 4-channel RGBA image.

    Parameters
    ----------
    image: np.ndarray
        The 3-channel RGB image array.
    backend: str
        The backend library to use for this conversion.

    Returns
    -------
    np.ndarray
        The 4-channel RGBA image array with the alpha value set to 255.
    """

    if image.shape[0] == 3:
        _, height, width = image.shape
    elif image.shape[-1] == 3:
        height, width, _ = image.shape
    else:
        return image

    if backend == "hal":
        try:
            import edgefirst_python  # type: ignore
        except ImportError:
            raise ImportError(
                "EdgeFirst HAL is needed to perform RGB to RGBA conversion.")

        src = edgefirst_python.TensorImage(
            width, height, fourcc=edgefirst_python.FourCC.RGB)
        src.copy_from_numpy(image)

        dst = edgefirst_python.TensorImage(
            width, height, fourcc=edgefirst_python.FourCC.RGBA)
        CONVERTER.convert(src, dst)

        im = np.zeros((dst.height, dst.width, 4), dtype=np.uint8)
        dst.normalize_to_numpy(im)
        return im
    else:
        alpha_channel = np.full((height, width, 1), 255, dtype=np.uint8)
        return np.concatenate((image, alpha_channel), axis=-1)


def imagenet(image: np.ndarray) -> np.ndarray:
    """
    Normalize the image with imagenet normalization.

    Parameters
    ----------
    image: np.ndarray
        The image RGB array with shape
        (3, height, width) or (height, width, 3).

    Returns
    -------
    np.ndarray
        The image with imagenet normalization.
    """
    mean = np.array([0.079, 0.05, 0]) + 0.406
    std = np.array([0.005, 0, 0.001]) + 0.224

    if image.shape[0] == 3:
        for channel in range(image.shape[0]):
            image[channel, :, :] = (image[channel, :, :] / 255
                                    - mean[channel]) / std[channel]
    else:
        for channel in range(image.shape[2]):
            image[:, :, channel] = (image[:, :, channel] / 255
                                    - mean[channel]) / std[channel]
    return image


def image_normalization(
    image: np.ndarray,
    normalization: str,
    input_type: np.dtype = np.float32
):
    """
    Performs image normalizations (signed, unsigned, raw).

    Parameters
    ----------
    image: np.ndarray
        The image to perform normalization.
    normalization: str
        This is the type of normalization to perform
        ("signed", "unsigned", "raw", "imagenet").
    input_type: str
        This is the NumPy datatype to convert. Ex. "uint8"

    Returns
    -------
    np.ndarray
        Depending on the normalization, the image will be returned.
    """
    if normalization.lower() == 'signed':
        return ((image.astype(np.float32) / 127.5) - 1.0).astype(input_type)
    elif normalization.lower() == 'unsigned':
        return (image.astype(np.float32) /
                255.0).astype(input_type)
    elif normalization.lower() == 'imagenet':
        return (imagenet(image.astype(np.float32))).astype(input_type)
    else:
        return (image).astype(input_type)


def crop_image(image: np.ndarray, box: Union[list, np.ndarray]) -> np.ndarray:
    """
    Crops the image to only the area that is covered by
    the box provided. This is primarily used in pose validation.

    Parameters
    ----------
    image: np.ndarray
        The frame to crop before feeding to the model.
    box: Union[list, np.ndarray]
        This contains non-normalized [xmin, ymin, xmax, ymax].

    Returns
    -------
    np.ndarray
        The image cropped to the area of the bounding box.
    """
    x1, y1, x2, y2 = box
    box_area = image[y1:y2, x1:x2, ...]
    return box_area


def rotate_image(data: Union[bytes, str]) -> Image.Image:
    """
    Read from the ImageExif to apply rotation on the image.

    Parameters
    ----------
    data: Union[bytes, str]
        Read image file as a bytes object or a string path
        to the image file.

    Returns
    -------
    Image.Image
        The pillow Image with rotation applied.
    """
    if isinstance(data, bytes):
        data = BytesIO(data)
    try:
        image = Image.open(data)
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = dict(image._getexif().items())

        if exif[orientation] == 3:
            image = image.transpose(Image.ROTATE_180)
        elif exif[orientation] == 6:
            image = image.transpose(Image.ROTATE_270)
        elif exif[orientation] == 8:
            image = image.transpose(Image.ROTATE_90)
    except (AttributeError, KeyError, IndexError):
        # cases: image don't have getexif
        image = Image.open(data).convert('RGB')
    return image


def resize(
    image: Union[TensorImage, np.ndarray],
    size: tuple = None,
    backend: str = "hal"
) -> np.ndarray:
    """
    Resizes the images with the specified dimension using
    the EdgeFirst Tensor API. The original aspect ratio is not maintained.
    Image needs to be uint8.

    Parameters
    ----------
    image: Union[edgefirst_python.TensorImage, np.ndarray]
        The image (RGB, RGBA, Gray) tensor with uint8 dtype.
    size: tuple
        Specify the (width, height) size of the new image.
    backend: str
        Specify the backend library for resizing the image from the options
        "hal", "opencv", "pillow".

    Returns
    -------
    np.ndarray
        Resized image.
    """
    if size is None:
        return image

    if backend == "hal":
        try:
            import edgefirst_python  # type: ignore
        except ImportError:
            raise ImportError(
                "EdgeFirst HAL is needed to resize using hal.")

        if isinstance(image, np.ndarray):
            # Array without any channels is assumed to be grey.
            if len(image.shape) == 2:
                fourcc = edgefirst_python.FourCC.GREY
                fourc = fourcc
                image = np.expand_dims(image, axis=-1)
                channels = 1
            else:
                # Currently OpenGL in x86_64 only supports RGBA.
                channels = 4
                fourcc = edgefirst_python.FourCC.RGBA
                if image.shape[-1] == 4:
                    fourc = edgefirst_python.FourCC.RGBA
                elif image.shape[-1] == 1:
                    fourcc = edgefirst_python.FourCC.GREY
                    fourc = fourcc
                    channels = 1
                else:
                    fourc = edgefirst_python.FourCC.RGB

            height, width, _ = image.shape
            src = edgefirst_python.TensorImage(width, height, fourcc=fourc)
            src.copy_from_numpy(image)
        else:
            src = image
            # Currently OpenGL in x86_64 only supports RGBA.
            fourcc = (edgefirst_python.FourCC.RGBA if
                      src.format == edgefirst_python.FourCC.RGB else src.format)
            channels = 1 if fourcc == edgefirst_python.FourCC.GREY else 4

        dst = edgefirst_python.TensorImage(size[0], size[1], fourcc=fourcc)
        CONVERTER.convert(src, dst)

        im = np.zeros((dst.height, dst.width, channels), dtype=np.uint8)
        dst.normalize_to_numpy(im)

        if src.format == edgefirst_python.FourCC.GREY:
            return im.squeeze()
        elif src.format == edgefirst_python.FourCC.RGB:
            return im[:, :, 0:3]
        return im
    elif backend == "opencv":
        try:
            import cv2  # type: ignore
        except ImportError:
            raise ImportError("OpenCV is needed to resize using opencv.")

        return cv2.resize(image, size, interpolation=cv2.INTER_LINEAR)
    else:
        image = Image.fromarray(np.uint8(image))
        image = image.resize(size)
        return np.array(image)


def pad(
    image: np.ndarray,
    input_size: tuple,
    backend: str = "hal"
) -> Tuple[np.ndarray, list]:
    """
    Performs image padding based on the implementation provided in YOLOx:\
    https://github.com/Megvii-BaseDetection/YOLOX/blob/main/yolox/data/data_augment.py#L142

    The image is always padded on the right and at the bottom portions.

    Parameters
    ----------
    image: np.ndarray
        This is the input image to pad.
    input_size: tuple
        This is the model input size (generally) or the output image
        resolution after padding in the order (height, width).
    backend: str
        Specify the backend library for resizing the image from the options
        "hal", "opencv", "pillow".

    Returns
    --------
    image: np.ndarray
        This is the padded image.
    shapes: list
        This is used to scale the bounding boxes of the ground
        truth and the model detections based on the letterbox
        transformation.
        [[pad image height, pad image width],
        [[scale_y, scale_x], [pad x, pad y]].
    """
    height, width = image.shape[:2]  # current shape [height, width]
    if len(image.shape) == 3:
        padded_image = np.ones(
            (input_size[0], input_size[1], 3), dtype=np.uint8) * 114
    else:
        padded_image = np.ones(input_size, dtype=np.uint8) * 114

    r = min(input_size[0] / height, input_size[1] / width)
    resized_image = resize(
        image, (int(width * r), int(height * r)), backend=backend
    )
    padded_image[: int(height * r),
                 : int(width * r)] = resized_image
    padded_image = rgb2bgr(padded_image)  # RGB2BGR
    padded_image = np.ascontiguousarray(padded_image)

    # The bounding box offset to add due to image padding.
    # Requires normalization due to the bounding boxes are already normalized.
    new_unpad = int(round(height * r)), int(round(width * r))
    dw = (padded_image.shape[1] - new_unpad[1])  # / new_unpad[1]
    dh = (padded_image.shape[0] - new_unpad[0])  # / new_unpad[0]

    # The image was not rescaled, so default to 1.0.
    shapes = [
        # imgsz (model input shape) [height, width]
        [padded_image.shape[0], padded_image.shape[1]],
        [[resized_image.shape[0] / input_size[0],
          resized_image.shape[1] / input_size[1]],
         [dw, dh]]  # ratio_pad [[scale y, scale x], [pad w, pad h]]
    ]
    return padded_image, shapes


def letterbox_native(
    image: np.ndarray,
    new_shape: tuple = (640, 640),
    constant: int = 114,
    backend: str = "hal"
) -> Tuple[np.ndarray, list]:
    """
    Applies the letterbox image transformations based in YOLOv5 and YOLOv7.

    Parameters
    ----------
    image : np.ndarray
        Input image array (HWC format).
    new_shape : tuple, optional
        Target shape (height, width) for output image, by default (640, 640).
    constant : int, optional
        Padding pixel value (0–255), by default 114 (gray).
    backend: str
        Specify the backend library for letterboxing the
        image from the options "opencv", "pillow".

    Returns
    -------
    image: np.ndarray
        The resized and padded image in HWC format.
    shapes: list
        This is used to scale the bounding boxes of the ground
        truth and the model detections based on the letterbox
        transformation. Tuple containing padded image size, scale ratio,
        and padding offsets.
        [[pad image height, pad image width],
        [[scale_y, scale_x], [pad x, pad y]]].
    """
    height, width = image.shape[:2]
    scale = min(new_shape[1] / width, new_shape[0] / height)
    new_width = int(round(width * scale))
    new_height = int(round(height * scale))

    if scale != 1.0:
        image = resize(image, (new_width, new_height), backend=backend)

    # Compute padding
    dw, dh = new_shape[1] - new_width, new_shape[0] - new_height  # wh padding
    top = round(dh / 2)
    bottom = dh - top
    left = round(dw / 2)
    right = dw - left

    if backend == "opencv":
        try:
            import cv2  # type: ignore
        except ImportError:
            raise ImportError("OpenCV is needed for letterbox.")

        padded_image = cv2.copyMakeBorder(
            image, top, bottom, left, right, cv2.BORDER_CONSTANT,
            value=(constant, constant, constant))  # add border
    else:
        padded_image = np.zeros(
            (3, new_height + top + bottom, new_width + left + right))
        for i, _ in enumerate(padded_image):
            padded_image[i, :, :] = np.pad(
                image[:, :, i], ((top, bottom), (left, right)),
                mode='constant', constant_values=constant)
        padded_image = np.transpose(
            padded_image, axes=(1, 2, 0)).astype(np.uint8)

    shapes = [
        # imgsz (model input shape) [height, width]
        [padded_image.shape[0], padded_image.shape[1]],
        # ratio_pad [[scale y, scale x], [pad w, pad h]]
        [[scale, scale], [left, top]]
    ]
    return padded_image, shapes


def letterbox_hal(
    image: TensorImage,
    dst: TensorImage,
) -> list:
    """
    Applies the letterbox image transformations using HAL.

    Parameters
    ----------
    image: TensorImage
        An RGBA tensor image loaded using the HAL.
    dst: TensorImage
        The destination tensor image after letterbox transformation.

    Returns
    -------
    label_ratio: list
        Scaling factors (width, height) applied to original boxes.
    shapes: list
        This is used to scale the bounding boxes of the ground
        truth and the model detections based on the letterbox
        transformation. Tuple containing padded image size, scale ratio,
        and padding offsets.
        [[pad image height, pad image width],
        [[scale_y, scale_x], [pad x, pad y]]].
    """

    try:
        import edgefirst_python  # type: ignore
    except ImportError:
        raise ImportError(
            "EdgeFirst HAL is needed to perform letterbox using hal.")

    ratio = min(dst.height / image.height, dst.width / image.width)
    height = image.height * ratio
    width = image.width * ratio
    top = round((dst.height - height) / 2)
    left = round((dst.width - width) / 2)
    height = round(height)
    width = round(width)

    CONVERTER.convert(image, dst,
                      dst_crop=edgefirst_python.Rect(left, top, width, height),
                      dst_color=[114, 114, 114, 255])

    shapes = [
        # imgsz (model input shape) [height, width]
        [dst.height, dst.width],
        # ratio_pad [[scale y, scale x], [pad w, pad h]]
        [[ratio, ratio], [left, top]]
    ]

    return shapes


def preprocess_hal(
    image: TensorImage,
    shape: tuple,
    input_type: np.dtype,
    dst: TensorImage,
    transpose: bool = False,
    input_tensor: Callable = None,
    preprocessing: str = "letterbox",
    normalization: str = "unsigned",
    quantization: tuple = None,
    visualize: bool = False
) -> Tuple[np.ndarray, np.ndarray, list, tuple]:
    """
    Optimized input preprocessing using the HAL.

    Parameters
    ----------
    image: TensorImage
        The image input to preprocess.
    shape: tuple
        The model input shape. This can either be formatted as
        (batch size, channels, height, width) or
        (batch size, height, width, channels).
    input_type: np.dtype
        The input datatype of the model.
    dst: TensorImage
        Destination tensor for placing the image transformations.
    transpose: bool
        Condition of whether to transpose the image or not. This
        is True for input shapes with channels first. Otherwise it is False.
    input_tensor: Callable
        Callable function for retrieving the input view tensor
        from the model for directly copying the input tensor
        into the model such as the case for TFLite.
    preprocessing: str
        The type of image preprocessing to apply. By default 'letterbox'
        is used. However, 'resize' or 'pad' are possible variations.
    normalization: str
        The type of image normalization to apply. Default is set to
        'unsigned'. However 'signed', 'raw', and 'imagenet' are possible
        values.
    quantization: tuple
        The quantization parameters of the input containing
        the (scale, zero point) values.
    visualize: bool
        When visualizing the model outputs, this requires a second
        copy of the transformed image. By default,
        visualization is set to False.

    Returns
    -------
    image: np.ndarray
        The image input after being preprocessed.
    visual_image: np.ndarray
        The image that is used for visualization post
        letterbox, padding, resize transformations.
    shapes: list
        This is used to scale the bounding boxes of the ground
        truth and the model detections based on the letterbox/padding
        transformation.

        .. code-block:: python

            [[input_height, input_width],
            [[scale_y, scale_x], [pad_w, pad_h]]]
    image_shape: tuple
        The original image dimensions.
    """

    try:
        import edgefirst_python  # type: ignore
    except ImportError:
        raise ImportError(
            "EdgeFirst HAL is needed to perform preprocessing using hal.")

    # Fetch only (height, width) from the shape.
    # Format for YUYV, RGB, and RGBA
    if shape[-1] in [2, 3, 4]:
        channels = shape[-1]
        shape = shape[1:3]
    else:
        channels = shape[1]
        shape = shape[2:4]

    height, width = image.height, image.width
    shapes = [
        # imgsz (model input shape) [height, width]
        [int(shape[0]), int(shape[1])],
        [[float(shape[0] / height), float(shape[1] / width)],
         [0.0, 0.0]]  # ratio_pad [image_scale, [pad w, pad h]]
    ]

    if preprocessing == "letterbox":
        shapes = letterbox_hal(image, dst)
    elif preprocessing == "pad":
        raise NotImplementedError("Padding with HAL is not yet implemented.")
    else:
        CONVERTER.convert(image, dst)

    if transpose:
        image = np.zeros([channels, dst.height, dst.width], dtype=input_type)
    else:
        image = np.zeros([dst.height, dst.width, channels], dtype=input_type)

    if input_type in [np.float16, np.float32]:
        if normalization == "unsigned":
            normalization = edgefirst_python.Normalization.UNSIGNED
        elif normalization == "signed":
            normalization = edgefirst_python.Normalization.SIGNED
        elif normalization == "raw":
            normalization = edgefirst_python.Normalization.RAW
        elif normalization == "imagenet":
            raise NotImplementedError(
                "ImageNet normalization is currently not implemented in HAL.")
        else:
            normalization = edgefirst_python.Normalization.DEFAULT
    else:
        normalization = edgefirst_python.Normalization.DEFAULT

    zero_point = None
    if quantization is not None:
        if input_type == np.int8:
            zero_point = abs(quantization[-1])
    # Directly copy the input tensor into the model for TFLite.
    if input_tensor is not None:
        dst.normalize_to_numpy(input_tensor()[0, :, :, :],
                               normalization=normalization,
                               zero_point=zero_point)
    else:
        # NOTE: PLANAR_RGBA is not yet supported in HAL.
        if transpose and channels == 4:
            dst.normalize_to_numpy(image[0:3, :, :], normalization=normalization,
                                   zero_point=zero_point)
        else:
            dst.normalize_to_numpy(image, normalization=normalization,
                                   zero_point=zero_point)

    visual_image = None
    if visualize:
        if transpose:
            visual_image = np.zeros([3, dst.height, dst.width], dtype=np.uint8)
            dst.normalize_to_numpy(visual_image)
            visual_image = np.transpose(visual_image, axes=[1, 2, 0])
        else:
            visual_image = np.zeros([dst.height, dst.width, 3], dtype=np.uint8)
            dst.normalize_to_numpy(visual_image)
    image = image[None]
    return image, visual_image, shapes, (height, width)


def preprocess_native(
    image: np.ndarray,
    shape: tuple,
    input_type: np.dtype,
    transpose: bool = False,
    input_tensor: Callable = None,
    preprocessing: str = "letterbox",
    normalization: str = "unsigned",
    quantization: tuple = None,
    backend: str = "hal",
) -> Tuple[np.ndarray, np.ndarray, list, tuple]:
    """
    Standard preprocessing method. Default parameters are based on
    Ultralytics defaults.

    Parameters
    ----------
    image: np.ndarray
        The image input to preprocess.
    shape: tuple
        The model input shape. This can either be formatted as
        (batch size, channels, height, width) or
        (batch size, height, width, channels).
    input_type: np.dtype
        The input datatype of the model.
    transpose: bool
        Condition of whether to transpose the image or not. This
        is True for input shapes with channels first. Otherwise it is False.
    input_tensor: Callable
        Callable function for retrieving the input view tensor
        from the model for directly copying the input tensor
        into the model such as the case for TFLite.
    preprocessing: str
        The type of image preprocessing to apply. By default 'letterbox'
        is used. However, 'resize' or 'pad' are possible variations.
    normalization: str
        The type of image normalization to apply. Default is set to
        'unsigned'. However 'signed', 'raw', and 'imagenet' are possible
        values.
    quantization: tuple
        The quantization parameters of the input containing
        the (scale, zero point) values.
    backend: str
        Specify the backend library for letterboxing the
        image from the options "opencv", "pillow".

    Returns
    -------
    image: np.ndarray
        The image input after being preprocessed.
    visual_image: np.ndarray
        The image that is used for visualization post
        letterbox, padding, resize transformations.
    shapes: list
        This is used to scale the bounding boxes of the ground
        truth and the model detections based on the letterbox/padding
        transformation.

        .. code-block:: python

            [[input_height, input_width],
            [[scale_y, scale_x], [pad_w, pad_h]]]
    image_shape: tuple
        The original image dimensions.
    """

    # Fetch only (height, width) from the shape.
    # Format for YUYV, RGB, and RGBA
    if shape[-1] in [2, 3, 4]:
        channel = shape[-1]
        shape = shape[1:3]
    else:
        channel = shape[1]
        shape = shape[2:4]
        # Transpose the image to meet requirements of the channel order.

    transformer = None  # Function that transforms image formats.
    if channel == 2:
        transformer = rgb2yuyv
    elif channel == 4:
        transformer = rgb2rgba

    height, width = image.shape[0:2]

    shapes = [
        shape,  # imgsz (model input shape) [height, width]
        [[shape[0] / height, shape[1] / width],
         [0.0, 0.0]]  # ratio_pad [image_scale, [pad w, pad h]]
    ]

    if backend == "opencv":
        # OpenCV reads images into BGR by default.
        image = bgr2rgb(image)

    if preprocessing == "letterbox":
        image, shapes = letterbox_native(
            image, new_shape=shape, backend=backend)
    elif preprocessing == "pad":
        image, shapes = pad(image, shape, backend=backend)
    else:
        image = resize(image, (shape[1], shape[0]), backend=backend)

    visual_image = image
    if preprocessing == "pad":
        visual_image = bgr2rgb(visual_image)

    # Convert image format to either YUYV, RGBA or keep as RGB.
    image = transformer(image, backend=backend) if transformer else image

    # Expects batch size, channel, height, width.
    if transpose:
        image = np.transpose(image, axes=[2, 0, 1])

    # Handle full/half precision input types.
    if input_type in [np.float16, np.float32]:
        image = image_normalization(image, normalization, input_type)

    # For quantized models, run input quantization parameters.
    if quantization is not None:
        if input_type == np.int8:
            zero_point = abs(quantization[-1])
            image = (image.astype(np.int16) - zero_point).astype(np.int8)

    image = image[None]
    # Directly copy the input tensor into the model for TFLite.
    if input_tensor is not None:
        np.copyto(input_tensor(), image)

    return image, visual_image, shapes, (height, width)


# Functions for Annotation Transformations

def clamp(
    value: Union[float, int],
    min: Union[float, int] = 0,
    max: Union[float, int] = 1
) -> Union[float, int]:
    """
    Clamps a given value between 0 and 1 by default.
    If the value is in between the set min and max, then it is returned.
    Otherwise it returns either min or max depending on which is the closest.

    Parameters
    ----------
    value: Union[float, int]
        Value to clamp between 0 and 1 (default).
    min: Union[float, int]
        Minimum acceptable value. Default to 0.
    max: Union[float, int]
        Maximum acceptable value. Default to 1.

    Returns
    -------
    Union[float, int]
        This is the clamped value.
    """
    return min if value < min else max if value > max else value


def standardize_coco_labels(labels: Union[list, np.ndarray]) -> list:
    """
    Converts synonyms of COCO labels to standard COCO labels using the
    provided labels mapping "COCO_LABEL_SYNC". This requires that the labels
    provided contain strings.

    Parameters
    ----------
    labels: Union[list, np.ndarray]
        This contains a list of string labels to map to
        standard COCO labels.

    Returns
    -------
    list
        Converted string labels to standard COCO labels.
    """
    synced_labels = list()
    for label in labels:
        for key in COCO_LABEL_SYNC.keys():
            if label == key:
                label = COCO_LABEL_SYNC[key]
        synced_labels.append(label)
    return synced_labels


def labels2string(
    int_labels: Union[list, np.ndarray],
    string_labels: Union[list, np.ndarray]
) -> list:
    """
    Converts label indices into their string represenations.

    Parameters
    ----------
    int_labels: Union[list, np.ndarray]
        A list of integer labels as indices to convert into strings.
    string_labels: Union[list, np.ndarray]
        A list of unique string labels used to map the label
        indices into their string representations.

    Returns
    -------
    list
        A list of string labels.
    """
    labels = []
    for label in int_labels:
        labels.append(string_labels[int(label)] if isinstance(
            label, (numbers.Number, np.ndarray)) else label)
    return labels


def normalize(boxes: np.ndarray, shape: tuple = None) -> np.ndarray:
    """
    Normalizes the boxes to the width and height
    of the image or model input resolution.

    Parameters
    ----------
    boxes: np.ndarray
        Contains bounding boxes to normalize [[boxes1], [boxes2]].
    shape: tuple
        The (height, width) shape of the image to normalize the annotations.

    Returns
    -------
    np.ndarray
        new x-coordinate = old x-coordinate / width
        new y-coordinate = old y-coordinate / height
    """
    if shape is None:
        return boxes

    if isinstance(boxes, list):
        boxes = np.array(boxes)
    boxes[..., 0:1] /= shape[1]
    boxes[..., 1:2] /= shape[0]
    boxes[..., 2:3] /= shape[1]
    boxes[..., 3:4] /= shape[0]
    return boxes


def denormalize(boxes: np.ndarray, shape: tuple = None) -> np.ndarray:
    """
    Denormalizes the boxes by the width and height of the image
    or model input resolution to get the pixel values of the boxes.

    Parameters
    ----------
    boxes: np.ndarray
        Contains bounding boxes to denormalize [[boxes1], [boxes2]].
    shape: tuple
        The (height, width) shape of the image to denormalize the annotations.

    Returns
    -------
    np.ndarray
        Denormalized set of bounding boxes in pixels values.
    """
    if shape is None:
        return boxes

    if isinstance(boxes, list):
        boxes = np.array(boxes)
    boxes[..., 0:1] *= shape[1]
    boxes[..., 1:2] *= shape[0]
    boxes[..., 2:3] *= shape[1]
    boxes[..., 3:4] *= shape[0]
    return boxes.astype(np.int32)


def normalize_polygon(vertex: Union[list, np.ndarray], shape: tuple) -> list:
    """
    Normalizes the vertex coordinate of a polygon.

    Parameters
    ----------
    vertex: Union[list, np.ndarray]
        This contains [x, y] coordinate.
    shape: tuple
        The (height, width) shape of the image to normalize the annotations.

    Returns
    -------
    list
        This contains normalized [x, y] coordinates.
    """
    return [float(vertex[0]) / shape[1], float(vertex[1]) / shape[0]]


def denormalize_polygon(vertex: Union[list, np.ndarray], shape: tuple) -> list:
    """
    Denormalizes the vertex coordinate of a polygon.

    Parameters
    ----------
    vertex: Union[list, np.ndarray]
        This contains [x, y] coordinate.
    shape: tuple
        The (height, width) shape of the image to denormalize the annotations.

    Returns
    -------
    list
        This contains denormalized [x, y] coordinates.
    """
    return [int(float(vertex[0]) * shape[1]), int(float(vertex[1]) * shape[0])]


def xcycwh2xyxy(boxes: np.ndarray) -> np.ndarray:
    """
    Converts YOLO (xcycwh) format into PascalVOC (xyxy) format.

    Parameters
    ----------
    boxes: np.ndarray
        Contains lists for each boxes in YOLO format [[boxes1], [boxes2]].

    Returns
    -------
    np.ndarray
        Contains list for each boxes in PascalVOC format.
    """
    return np.concatenate([
        boxes[:, 0:2] - boxes[:, 2:4] / 2,
        boxes[:, 0:2] + boxes[:, 2:4] / 2
    ], axis=1)


def xyxy2xcycwh(boxes: np.ndarray) -> np.ndarray:
    """
    Converts PascalVOC (xyxy) into YOLO (xcycwh) format.

    Parameters
    ----------
    boxes: np.ndarray
        Contains lists for each boxes in PascalVOC format [[boxes1], [boxes2]].

    Returns
    -------
    np.ndarray
        Contains list for each boxes in YOLO format.
    """
    w_c = boxes[..., 2:3] - boxes[..., 0:1]
    h_c = boxes[..., 3:4] - boxes[..., 1:2]
    boxes[..., 0:1] = boxes[..., 0:1] + w_c / 2
    boxes[..., 1:2] = boxes[..., 1:2] + h_c / 2
    boxes[..., 2:3] = w_c
    boxes[..., 3:4] = h_c
    return boxes


def xywh2xyxy(boxes: np.ndarray) -> np.ndarray:
    """
    Converts COCO (xywh) format to PascalVOC (xyxy) format.

    Parameters
    ----------
    boxes: np.ndarray
        Contains lists for each boxes in COCO format [[boxes1], [boxes2]].

    Returns
    -------
    np.ndarray
        Contains list for each boxes in PascalVOC format.
    """
    boxes[..., 2:3] = boxes[..., 2:3] + boxes[..., 0:1]
    boxes[..., 3:4] = boxes[..., 3:4] + boxes[..., 1:2]
    return boxes


def xyxy2xywh(boxes: np.ndarray) -> np.ndarray:
    """
    Converts PascalVOC (xyxy) format to COCO (xywh) format.

    Parameters
    ----------
    boxes: np.ndarray
        Contains lists for each boxes in COCO format [[boxes1], [boxes2]].

    Returns
    -------
    np.ndarray
        Contains list of each boxes in COCO format.
    """
    boxes[..., 2:3] = boxes[..., 2:3] - boxes[..., 0:1]
    boxes[..., 3:4] = boxes[..., 3:4] - boxes[..., 1:2]
    return boxes


def scale(
    boxes: np.ndarray,
    w: int = 640,
    h: int = 640,
    padw: int = 0,
    padh: int = 0,
) -> np.ndarray:
    """
    Scales the bounding boxes to be centered around the objects of an image
    with letterbox transformation.

    Parameters
    ----------
    boxes: np.ndarray (nx4)
        This is already in xyxy format.
    w: int
        This is the width of the image before any letterbox
        transformation.
    h: int
        This is the height of the image before any letterbox
        transformation.
    padw: int
        The width padding in relation to the letterbox.
    padh: int
        The height padding in relation to the letterbox.

    Returns
    -------
    np.ndarray
        The bounding boxes rescaled to be centered around the
        objects of an image with letterbox transformation.
    """
    y = np.copy(boxes)
    y[..., 0] = (w * (boxes[..., 0]) + padw)  # top left boxes
    y[..., 1] = (h * (boxes[..., 1]) + padh)  # top left y
    y[..., 2] = (w * (boxes[..., 2]) + padw)  # bottom right boxes
    y[..., 3] = (h * (boxes[..., 3]) + padh)  # bottom right y
    return y


def clamp_boxes(boxes: np.ndarray, clamp: int,
                shape: tuple = None) -> np.ndarray:
    """
    Clamps bounding boxes with size less than the provided clamp value to
    the clamp value in pixels. The minimum width and height  (dimensions)
    of the bounding is the clamp value in pixels.

    Parameters
    ----------
    boxes: np.ndarray
        The bounding boxes to clamp. The bounding boxes with dimensions
        larger than the clamp value will be kept, but the smaller boxes will
        be resized to the clamp value.
    clamp: int
        The minimum dimensions allowed for the height and width of the
        bounding box. This value is in pixels.
    shape: tuple
        If None is provided (by default), it assumes the boxes are in pixels.
        Otherwise, if shape is provided, the boxes are normalized which
        will transform the boxes in pixel representations first to be
        compared to the clamp value provided which is in pixels. The
        shape provided should be the (height, width) of the image.

    Returns
    -------
    np.ndarray
        The bounding boxes where the smaller boxes have been
        sized to the clamp value provided.
    """
    if len(boxes) == 0:
        return boxes

    if shape is None:
        height, width = (1, 1)
    else:
        height, width = shape

    widths = ((boxes[..., 2:3] - boxes[..., 0:1]) * width).flatten()
    heights = ((boxes[..., 3:4] - boxes[..., 1:2]) * height).flatten()
    modify = np.transpose(
        np.nonzero(((widths < clamp) + (heights < clamp)))).flatten()

    boxes[modify, 2:3] = boxes[modify, 0:1] + clamp / width
    boxes[modify, 3:4] = boxes[modify, 1:2] + clamp / height
    return boxes


def ignore_boxes(
    ignore: int,
    boxes: np.ndarray,
    labels: np.ndarray,
    scores: np.ndarray = None,
    shape: tuple = None
) -> Tuple[np.ndarray, np.ndarray, Union[None, np.ndarray]]:
    """
    Removes the boxes, labels, and scores provided if the boxes have dimensions
    less than the provided value set by the ignore parameter in pixels.

    Parameters
    ----------
    ignore: int
        The size of the boxes lower than this value will be removed. This
        value is in pixels.
    boxes: np.ndarray
        The bounding boxes array with shape (n, 4). The bounding boxes with
        dimensions less than the ignore parameter will be removed.
    labels: np.ndarray
        The labels associated to each bounding box. For every bounding box
        that was removed, the labels will also be removed.
    scores: np.ndarray
        (Optional) the scores associated to each bounding box. For every
        bounding box that was removed, the scores will also be removed.
    shape: tuple
        If None is provided (by default), it assumes the boxes are in pixels.
        Otherwise, if shape is provided, the boxes are normalized which
        will transform the boxes in pixel representations first to be
        compared to the ignore value provided which is in pixels. The
        shape provided should be the (height, width) of the image.

    Returns
    -------
    boxes: np.ndarray
        The bounding boxes where the smaller boxes have been removed.
    labels: np.ndarray
        The labels which contains only the labels of
        the existing bounding boxes.
    scores: Union[None, np.ndarray]
        If scores is not provided, None is returned. Otherwise,
        the scores of the returned bounding boxes are returned.
    """
    if shape is None:
        height, width = (1, 1)
    else:
        height, width = shape

    widths = ((boxes[..., 2:3] - boxes[..., 0:1]) * width).flatten()
    heights = ((boxes[..., 3:4] - boxes[..., 1:2]) * height).flatten()
    keep = np.transpose(
        np.nonzero(((widths >= ignore) * (heights >= ignore)))).flatten()

    boxes = np.take(boxes, keep, axis=0)
    labels = np.take(labels, keep, axis=0)
    if scores is not None:
        scores = np.take(scores, keep, axis=0)

    return boxes, labels, scores

# Functions for Segmentation Transformations


def segments2boxes(segments: list, box_format: str = "xcycwh") -> np.ndarray:
    """
    Convert segment labels to box labels, i.e.
    (xy1, xy2, ...) to (xcycwh).

    Parameters
    ----------
    segments: list
        List of segments where each segment is a list of points,
        each point is [x, y] coordinates.
    box_format: str
        Default output box format is in "xcycwh" (YOLO) format.
        Otherwise, "xywh" (COCO) and "xyxy" (PascalVOC) are also accepted.

    Returns
    -------
    np.ndarray
        Bounding box coordinates in YOLO format.
    """
    boxes = []
    for s in segments:
        x, y = s.T  # segment xy
        boxes.append([x.min(), y.min(), x.max(), y.max()])  # xyxy

    if box_format == "xcycwh":
        return xyxy2xcycwh(np.array(boxes))  # cls, xywh
    elif box_format == "xywh":
        return xyxy2xywh(np.array(boxes))
    else:
        return np.array(boxes)


def resample_segments(segments: list, n: int = 1000) -> list:
    """
    Resample segments to n points each using linear interpolation.
    Source: https://github.com/ultralytics/ultralytics/blob/main/ultralytics/utils/ops.py#L485

    Parameters
    ----------
    segments: list
        List of (N, 2) arrays where N is the number of points in each segment.
    n: int
        Number of points to resample each segment to.

    Returns
    -------
    list
        Resampled segments with n points each.
    """
    for i, s in enumerate(segments):
        if len(s) == n:
            continue
        s = np.concatenate((s, s[0:1, :]), axis=0)
        x = np.linspace(0, len(s) - 1, n - len(s) if len(s) < n else n)
        xp = np.arange(len(s))
        x = np.insert(x, np.searchsorted(x, xp), xp) if len(s) < n else x
        segments[i] = (
            np.concatenate([np.interp(x, xp, s[:, i])
                            for i in range(2)], dtype=np.float32).reshape(2, -1).T
        )  # segment xy
    return segments


def format_segments(
    segments: np.ndarray,
    shape: tuple,
    ratio_pad: tuple,
    colors: Union[list, np.ndarray],
    mask_ratio: int = 1,
    semantic: bool = False,
    backend: str = "hal"
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convert polygon segments to bitmap masks.

    Parameters
    ----------
    segments: np.ndarray
        Mask segments with shape (# polygons, # coordinates, 2)
    shape: tuple
        This represents the (height, width) of the model input shape.
    ratio_pad: tuple
        This contains the scale and the padding factors after letterbox
        transformations in the form ((scale x, scale y), (pad x, pad y)).
    colors: Union[list, np.ndarray]
        The label to specify to each polygon.
    mask_ratio: int, optional
        Masks are downsampled according to mask_ratio. Set to 1 so
        that the output shape of the mask matches the model prediction shape.
    semantic: bool, optional
        Specify if the type of segmentation is semantic segmentation.
        By default this is False and set to instance segmentation as
        seen in Ultralytics. Instance segmentation is where
        each mask is represented separately.
    backend: str
        Specify the backend library for resizing the image from the options
        "hal", "opencv", "pillow".

    Returns
    -------
    masks: np.ndarray
        Bitmap masks with shape (N, H, W) or (1, H, W)
        if mask_overlap is True.
    sorted_idx: np.ndarray
        Resorting the ground truth based on these indices.
    """
    scale_h, scale_w = ratio_pad[0]
    padw, padh = ratio_pad[1]

    if len(segments):
        segments[..., 0] *= scale_w
        segments[..., 1] *= scale_h
        segments[..., 0] += padw
        segments[..., 1] += padh

    sorted_idx = None

    if semantic:
        masks = create_mask_image(
            polygons=segments,
            labels=colors,
            shape=shape
        )
    else:
        masks = polygons2masks(
            imgsz=shape,
            segments=segments,
            downsample_ratio=mask_ratio,
            backend=backend
        )
    return masks, sorted_idx


def polygon2mask(
    imgsz: Tuple[int, int],
    polygons: List[np.ndarray],
    color: int = 1,
    downsample_ratio: int = 1,
    backend: str = "hal"
) -> np.ndarray:
    """
    Convert a list of polygons to a binary mask of the specified image size.

    Parameters
    ----------
    imgsz: Tuple[int, int]
        The size of the image as (height, width).
    polygons: List[np.ndarray]
        A list of polygons. Each polygon is an array with shape (N, M), where
        N is the number of polygons, and M is the number of points
        such that M % 2 = 0.
    color: int, optional
        The color value to fill in the polygons on the mask.
    downsample_ratio: int, optional
        Factor by which to downsample the mask.
    backend: str
        Specify the backend library for resizing the image from the options
        "hal", "opencv", "pillow".

    Returns
    -------
    np.ndarray
        A binary mask of the specified image size with the polygons filled in.
    """
    polygons = np.asarray(polygons, dtype=np.int32)
    polygons = polygons.reshape((polygons.shape[0], -1, 2))
    mask = create_mask_image(
        polygons=polygons,
        labels=color,
        shape=imgsz
    )

    if downsample_ratio > 1:
        nh, nw = (imgsz[0] // downsample_ratio, imgsz[1] // downsample_ratio)
        mask = resize(mask, (nw, nh), backend=backend)
    return mask


def polygons2masks(
    imgsz: Tuple[int, int],
    segments: List[np.ndarray],
    downsample_ratio: int = 1,
    backend: str = "hal"
) -> np.ndarray:
    """
    Convert a list of polygons to a set of binary instance
    segmentation masks at the specified image size.

    Parameters
    ----------
    imgsz: Tuple[int, int]
        The size of the image as (height, width).
    segments: List[np.ndarray]
        A list of polygons. Each polygon is an array with shape (N, M), where
        N is the number of polygons, and M is the number of points
        such that M % 2 = 0.
    colors: Union[list, np.ndarray]
        The color value to fill each polygon in the masks.
    downsample_ratio: int, optional
        Factor by which to downsample each mask.
    backend: str
        Specify the backend library for resizing the image from the options
        "hal", "opencv", "pillow".

    Returns
    -------
    np.ndarray
        A set of binary masks of the specified image size
        with the polygons filled in.
    """
    if len(segments) == 0:
        return np.zeros((1, imgsz[0], imgsz[1]), dtype=np.int32)
    return np.array([polygon2mask(imgsz, [x.reshape(-1)],
                                  downsample_ratio=downsample_ratio,
                                  backend=backend)
                     for x in segments])


def create_mask_image(
    polygons: Union[list, np.ndarray],
    labels: Union[list, np.ndarray, int],
    shape: tuple
) -> np.ndarray:
    """
    Creates a NumPy array of masks from a given list of polygons.

    Parameters
    ----------
    polygons: Union[list, np.ndarray]
        This contains the polygon points. Ex.
        [[[x1,y1], [x2,y2], ... ,[xn,yn]], [...], ...]
    labels: Union[list, np.ndarray, int]
        The integer label of each polygon for assigning the mask.
        If an integer is supplied, then a constant label is applied
        for all the polygons.
    shape: tuple
        This is the shape (height, width) of the mask.

    Returns
    -------
    np.ndarray
        The 2D mask image with shape (height, width) specified.
    """
    mask = Image.new('L', (shape[1], shape[0]), 0)
    canvas = ImageDraw.Draw(mask)
    polygons = polygons.tolist() if isinstance(polygons, np.ndarray) else polygons
    if isinstance(labels, (int, np.ScalarType)):
        labels = np.full(len(polygons), labels, dtype=np.int32)
    for c, polygon in zip(labels, polygons):
        polygon = [tuple(pt) for pt in polygon]  # requires a list of Tuples.
        if len(polygon) >= 2:
            canvas.polygon(polygon, outline=int(c), fill=int(c))
    # This array contains a mask of the image where the objects are
    # outlined by class number
    return np.array(mask)


def create_binary_mask(mask: np.ndarray) -> np.ndarray:
    """
    Creates a binary NumPy array of 1's and 0's encapsulating
    every object (regardless of class) in the image as a 1 and
    background as 0.

    Parameters
    ----------
    mask: np.ndarray
        2D array mask of class labels unique to each object.

    Returns
    -------
    np.ndarray
        Binary 2D mask of 1's and 0's.
    """
    return np.where(mask > 0, 1, mask)


def create_mask_class(mask: np.ndarray, cls: int) -> np.ndarray:
    """
    Separates a mask with more than one classes into an individual
    mask of 1's and 0's where 1 represents the specified class and
    0 represents other classes including background.

    Parameters
    ----------
    mask: np.ndarray
        Multiclass mask of class labels unique to each object.
    cls: int
        The integer representing the class in the mask
        to keep as a value of 1. The other classes will be treated as
        0's.

    Returns
    -------
    np.ndarray
        Binary 2D mask of 1's and 0's.
    """
    temp_mask = np.where(mask != cls, 0, mask)
    temp_mask[temp_mask == cls] = 1
    return temp_mask


def create_mask_classes(
    new_mask: np.ndarray,
    cls: int,
    current_mask: np.ndarray = None
) -> np.ndarray:
    """
    Appends a current mask with another mask of different class
    i.e converting a binary mask (new mask) into a mask with its
    class and then appending the original mask to include
    the new mask with its class.

    Parameters
    ----------
    new_mask: np.ndarray
        The current binary (0, 1) 2D mask.
    cls: int
        Class representing the 1's in the new mask. This is the class
        to append to the current mask.
    current_mask: (height, width) np.ndarray
        Current multiclass mask.

    Returns
    -------
    np.ndarray
        Multiclass mask with an additional class added.
    """
    new_mask = np.where(new_mask == 1, cls, new_mask)
    if current_mask is not None:
        return np.add(current_mask, new_mask)
    else:
        return new_mask


def create_mask_background(mask: np.ndarray) -> np.ndarray:
    """
    Creates a binary mask for the background class with 1's in the
    image and the rest of the objects will have values of 0's. This function
    switches the labels for background to 1 and positive classes to 0's.

    Parameters
    ----------
    mask: np.ndarray
        Multiclass mask array representing each image pixels.

    Returns
    -------
    np.ndarray
        Binary mask of 1's and 0's, where 1's is background and
        objects are 0's
    """
    # 2 is a temporary class
    temp_mask = np.where(mask != 0, 2, mask)
    temp_mask[temp_mask == 0] = 1
    temp_mask[temp_mask == 2] = 0
    return temp_mask


def convert_to_serializable(obj: Any):
    """
    Recursively convert NumPy types to
    Python-native types for JSON serialization.

    Parameters
    ----------
    obj: Any
        Any NumPy type.

    Returns
    -------
    obj
        The object with a native
        python type representation.
    """
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, np.generic):
        return obj.item()  # Convert other NumPy scalars
    elif isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return 0
    elif isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(i) for i in obj]
    else:
        return obj

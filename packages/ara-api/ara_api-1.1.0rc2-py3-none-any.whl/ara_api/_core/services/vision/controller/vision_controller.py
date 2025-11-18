"""Vision controller module for working with computer vision.

This module contains VisionController class that
handles computer vision operations. It's designed to work in a separate
subprocess due to OpenCV limitations with multiprocessing.

Classes:
    VisionController: Main class for computer vision operations
"""

import threading
import time
from typing import Dict, Optional, Tuple, Union

import cv2
import numpy as np

from ara_api._core.services.vision.controller.camera_controller import (
    CameraController,
)
from ara_api._utils import (
    Aruco,
    ArucoArray,
    Blob,
    BlobArray,
    CameraConfig,
    Image,
    Logger,
    QRCode,
    QRCodeArray,
)
from ara_api._utils.config import DETECTION_CONFIG


class VisionController:
    def __init__(self, logger: Logger):
        self._logger = logger
        self._camera_controller: CameraController = CameraController(logger)

        self._lock = threading.RLock()

        self._aruco_dict_types = {
            "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
            "DICT_4X4_100": cv2.aruco.DICT_4X4_100,
            "DICT_4X4_250": cv2.aruco.DICT_4X4_250,
            "DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
            "DICT_5X5_50": cv2.aruco.DICT_5X5_50,
            "DICT_5X5_100": cv2.aruco.DICT_5X5_100,
            "DICT_5X5_250": cv2.aruco.DICT_5X5_250,
            "DICT_5X5_1000": cv2.aruco.DICT_5X5_1000,
            "DICT_6X6_50": cv2.aruco.DICT_6X6_50,
            "DICT_6X6_100": cv2.aruco.DICT_6X6_100,
            "DICT_6X6_250": cv2.aruco.DICT_6X6_250,
            "DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
            "DICT_7X7_50": cv2.aruco.DICT_7X7_50,
            "DICT_7X7_100": cv2.aruco.DICT_7X7_100,
            "DICT_7X7_250": cv2.aruco.DICT_7X7_250,
            "DICT_7X7_1000": cv2.aruco.DICT_7X7_1000,
            "DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL,
            "DICT_APRILTAG_16h5": cv2.aruco.DICT_APRILTAG_16h5,
            "DICT_APRILTAG_25h9": cv2.aruco.DICT_APRILTAG_25h9,
            "DICT_APRILTAG_36h10": cv2.aruco.DICT_APRILTAG_36h10,
            "DICT_APRILTAG_36h11": cv2.aruco.DICT_APRILTAG_36h11,
        }

        self._aruco_detectors: Dict[str, cv2.aruco.ArucoDetector] = {}
        self._qr_detector = cv2.QRCodeDetector()

        self._default_aruco_params = cv2.aruco.DetectorParameters()

    def initialize(self, url: str = "0") -> bool:
        return self._camera_controller.initialize(url=url)

    def _get_image_data(
        self, image: Optional[Union[Image, np.ndarray]]
    ) -> Optional[np.ndarray]:
        if image is None:
            return self._camera_controller.read_frame()
        elif isinstance(image, Image):
            return image.data
        else:
            return image

    def _get_aruco_detector(
        self, dictionary_type: str
    ) -> cv2.aruco.ArucoDetector:
        if dictionary_type not in self._aruco_detectors:
            if dictionary_type in self._aruco_dict_types:
                dictoinary = cv2.aruco.getPredefinedDictionary(
                    self._aruco_dict_types[dictionary_type]
                )
            else:
                self._logger.warning(
                    "Unknown ArUco dictionary: {dict}, using default".format(
                        dict=dictionary_type
                    )
                )
                dictionary = cv2.aruco.getPredefinedDictionary(
                    cv2.aruco.DICT_ARUCO_ORIGINAL
                )

            self._aruco_detectors[dictionary_type] = cv2.aruco.ArucoDetector(
                dictionary, self._default_aruco_params
            )

        return self._aruco_detectors[dictionary_type]

    def get_current_frame(self) -> Optional[Image]:
        frame_data = self._camera_controller.read_frame()
        if frame_data is None:
            return None

        image = Image()
        image.sync(frame_data)
        return image

    def detect_aruco(
        self,
        image: Optional[Union[Image, np.ndarray]] = None,
        dictionary_type: Optional[str] = None,
        maarker_size: Optional[float] = None,
    ) -> ArucoArray:
        aruco_array = ArucoArray()
        dict_type = dictionary_type or DETECTION_CONFIG.ARUCO_DICT_TYPE
        size = maarker_size or DETECTION_CONFIG.ARUCO_MARKER_SIZE

        try:
            image_data = self._get_image_data(image)
            if image_data is None:
                self._logger.warning("Failed to get frame for ArUco detection")
                return aruco_array

            if len(image_data.shape) == 3:
                gray = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
            else:
                gray = image_data

            detector = self._get_aruco_detector(dict_type)

            corners, ids, _ = detector.detectMarkers(gray)

            if ids is None or len(ids) == 0:
                return aruco_array

            current_time = time.time()
            for i, marker_id in enumerate(ids):
                marker_corners = corners[i][0]

                aruco_marker = Aruco()

                center_x = float(np.mean(marker_corners[:, 0]))
                center_y = float(np.mean(marker_corners[:, 1]))

                edge_vector = marker_corners[1] - marker_corners[0]
                angle = float(np.arctan2(edge_vector[1], edge_vector[0]))

                marker_data = {
                    "id": int(marker_id[0]),
                    "corners": [
                        [float(x), float(y)] for x, y in marker_corners
                    ],
                    "center": [center_x, center_y],
                    "marker_size": size,
                    "dictionary": dict_type,
                    "timestamp": current_time,
                    "confidence": 1.0,  # Placeholder confidence
                    "position": {
                        "x": center_x,
                        "y": center_y,
                        "z": 0.0,
                    },
                    "orientation": {
                        "x": 0.0,
                        "y": 0.0,
                        "z": angle,
                    },
                }
                aruco_marker.sync(marker_data)
                aruco_array.add(aruco_marker)

            return aruco_array

        except Exception as e:
            self._logger.error(
                "Error detecting ArUco markers: {e}".format(e=e)
            )
            return aruco_array

    def detect_qr_code(
        self, image: Optional[Union[Image, np.ndarray]] = None
    ) -> QRCodeArray:
        qr_array = QRCodeArray()

        try:
            image_data = self._get_image_data(image)
            if image_data is None:
                self._logger.warning(
                    "Failed to get frame for QR code detection"
                )
                return qr_array

            retval, decoded_info, points, _ = (
                self._qr_detector.detectAndDecodeMulti(image_data)
            )

            if not retval or not decoded_info:
                return qr_array

            current_time = time.time()
            for i, data in enumerate(decoded_info):
                if not data:
                    continue

                qr_corners = points[i]
                qr_code = QRCode()

                center_x = float(np.mean(qr_corners[:, 0]))
                center_y = float(np.mean(qr_corners[:, 1]))

                qr_data = {
                    "data": data,
                    "corners": [[float(x), float(y)] for x, y in qr_corners],
                    "center": [center_x, center_y],
                    "position": {"x": center_x, "y": center_y, "z": 0.0},
                    "timestamp": current_time,
                    "confidence": 1.0,
                }

                qr_code.sync(qr_data)
                qr_array.add(qr_code)

            return qr_array
        except Exception as e:
            self._logger.error("Error detecting QR codes: {e}".format(e=e))
            return qr_array

    def detect_blobs(
        self,
        image: Optional[Union[Image, np.ndarray]] = None,
        lower_color: Optional[Tuple[int, int, int]] = None,
        upper_color: Optional[Tuple[int, int, int]] = None,
        min_area: Optional[float] = None,
        max_blobs: Optional[int] = None,
    ) -> BlobArray:
        blob_array = BlobArray()

        lower = lower_color or DETECTION_CONFIG.BLOB_LOWER_COLOR
        upper = upper_color or DETECTION_CONFIG.BLOB_UPPER_COLOR
        min_area_val = min_area or DETECTION_CONFIG.BLOB_MIN_AREA
        max_blobs_val = max_blobs or DETECTION_CONFIG.BLOB_MAX_BLOBS

        try:
            image_data = self._get_image_data(image)
            if image_data is None:
                self._logger.warning("Failed to get frame for blob detection")
                return blob_array

            mask = cv2.inRange(image_data, np.array(lower), np.array(upper))

            contours, _ = cv2.findContours(
                mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            current_time = time.time()
            blob_id = 0
            for contour in contours[:max_blobs_val]:
                area = cv2.contourArea(contour)
                if area < min_area_val:
                    continue

                M = cv2.moments(contour)
                if M["m00"] == 0:
                    continue

                center_x = int(M["m10"] / M["m00"])
                center_y = int(M["m01"] / M["m00"])

                x, y, w, h = cv2.boundingRect(contour)

                epsilon = 0.01 * cv2.arcLength(contour, True)
                countour_simple = cv2.approxPolyDP(contour, epsilon, True)

                contour_reshaped = countour_simple.reshape(-1, 2)
                contour_points = [
                    [float(x), float(y)] for x, y in contour_reshaped
                ]

                roi = image_data[y : y + h, x : x + w]
                avg_color = [float(np.mean(roi[:, :, i])) for i in range(3)]

                blob = Blob()

                blob_data = {
                    "id": blob_id,
                    "contour": contour_points,
                    "center": [center_x, center_y],
                    "position": {"x": center_x, "y": center_y, "z": 0.0},
                    "size": float(area),
                    "bounding_box": [int(x), int(y), int(w), int(h)],
                    "color": avg_color,
                    "timestamp": current_time,
                    "confidence": 1.0,
                }

                blob.sync(blob_data)
                blob_array.add(blob)
                blob_id += 1

            return blob_array

        except Exception as e:
            self._logger.error("Error detecting blobs: {e}".format(e=e))
            return blob_array

    @property
    def camera_controller(self) -> CameraController:
        return self._camera_controller

    def release_camera(self) -> None:
        self._camera_controller.release()

    def release(self) -> None:
        with self._lock:
            self.release_camera()
            self._aruco_detectors.clear()
            self._logger.info("VisionController resources released")

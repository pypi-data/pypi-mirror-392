import threading
from typing import Optional, Union

import cv2
import numpy as np

from ara_api._utils import CameraConfig, Logger


class CameraController:
    def __init__(self, logger: Logger):
        self._logger = logger
        self._capture: Optional[cv2.VideoCapture] = None
        self._is_connected = False

        self._lock = threading.Lock()

        self._camera_config = CameraConfig()

        cv2.setNumThreads(0)  # Disable OpenCV multithreading

    def initialize(self, url: str = "0") -> bool:
        try:
            self._logger.debug(
                "Initializing camera with URL '{url}'".format(url=url)
            )

            with self._lock:
                device_index: Union[int, str] = (
                    int(url) if url.isdigit() else url
                )

                if self._capture is not None:
                    self._capture.release()
                    self._capture = None

                self._capture = cv2.VideoCapture(device_index)

                if not self._capture.isOpened():
                    self._logger.error(
                        "Failed to open camera at {url}".format(url=url)
                    )
                    self._is_connected = False
                    self._capture = None
                    return False

                width = self._capture.get(cv2.CAP_PROP_FRAME_WIDTH)
                height = self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT)

                self._camera_config.sync(
                    {
                        "width": int(width),
                        "height": int(height),
                        "fps": int(self._capture.get(cv2.CAP_PROP_FPS)),
                        "url": device_index,
                        "intrinsics": {
                            "fx": width / 2,
                            "fy": height / 2,
                            "cx": width / 2,
                            "cy": height / 2,
                            "distortion": [0.0, 0.0, 0.0, 0.0, 0.0],
                        },
                        "brightness": self._capture.get(
                            cv2.CAP_PROP_BRIGHTNESS
                        ),
                        "contrast": self._capture.get(cv2.CAP_PROP_CONTRAST),
                        "saturation": self._capture.get(
                            cv2.CAP_PROP_SATURATION
                        ),
                    }
                )

                self._logger.info(
                    "Camera initialized successfully "
                    "with config: {config}".format(config=self._camera_config)
                )
                self._is_connected = True
                return True
        except Exception as e:
            self._logger.error("Error initializing camera: {e}".format(e=e))
            self._is_connected = False
            if self._capture is not None:
                self._capture.release()
                self._capture = None
            return False

    def read_frame(self) -> Optional[np.ndarray]:
        if not self._is_connected or self._capture is None:
            return None

        with self._lock:
            try:
                ret, frame = self._capture.read()
                if not ret or frame is None:
                    self._logger.warning("Failed to read frame from camera")
                    return None
                return frame
            except Exception as e:
                self._logger.error("Error reading frame: {e}".format(e=e))
                return None

    def release(self) -> None:
        with self._lock:
            if self._capture is not None:
                try:
                    self._capture.release()
                except Exception as e:
                    self._logger.warning(
                        "Error releasing camera {e}".format(e=e)
                    )
                finally:
                    self._capture = None
            self._is_connected = False
        self._logger.info("Camera released successfully")

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    @property
    def camera_config(self) -> CameraConfig:
        return self._camera_config

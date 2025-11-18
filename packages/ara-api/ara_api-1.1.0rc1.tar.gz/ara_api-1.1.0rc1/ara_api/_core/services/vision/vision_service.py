import argparse
import sys
import threading
from typing import Optional

import cv2
import grpc

from ara_api._core.services.vision.controller import VisionController
from ara_api._utils import Logger, VisionServicer


class VisionManager(VisionServicer):
    def __init__(self, log: bool = True, output: bool = True):
        self._vision_controller: Optional[VisionController] = None
        self._initialized = False
        self._lock: threading.Lock = threading.Lock()

        self._logger = Logger(
            log_to_file=log,
            log_to_terminal=output,
        )

        cv2.setNumThreads(0)
        self._logger.debug("OpenCV configured for single-threaded operation ")

    def initialize(self, url: str = "0") -> bool:
        with self._lock:
            if self._initialized:
                raise RuntimeError(
                    "VisionManager is already initialized. "
                    "Call release() before re-initializing"
                )

            try:
                self._logger.debug(
                    "Initializing VisionController with URL: {url}".format(
                        url=url
                    )
                )
                self._vision_controller = VisionController(self._logger)
                success = self._vision_controller.initialize(url=url)

                if success:
                    self._initialized = True
                    self._logger.info(
                        "VisionController initialized successfully"
                    )
                else:
                    self._initialized = False
                    self._logger.error(
                        "VisionController initialization failed"
                    )

                return success

            except Exception as e:
                self._logger.error(
                    "VisoionController initialization failed: {e}".format(e=e)
                )
                self._initialized = False
                return False

    def get_image_rpc(self, request, context):
        try:
            self._logger.debug(
                "[IMAGE] Request from client: {peer}".format(
                    peer=context.peer()
                )
            )
            self._logger.debug(
                "[IMAGE] Request details: {request}".format(request=request)
            )
            if not self.is_initialized or not self._vision_controller:
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                context.set_details("Vision system not initialized")
                self._logger.error(
                    "get_image_rpc called but vision system not initialized"
                )
                raise RuntimeError(
                    "Vision system not initialized. Call initialize() first."
                )

            self._logger.debug(
                "[IMAGE] Request from client: {peer}".format(
                    peer=context.peer()
                )
            )

            image = self._vision_controller.get_current_frame()
            if image is None:
                context.set_code(grpc.StatusCode.UNAVAILABLE)
                context.set_details("Failed to capture image from camera")
                self._logger.warning("Failed to capture image from camera")

            self._logger.debug(
                "[IMAGE] Detected image: {img}".format(img=image)
            )
            return image.grpc

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(
                "Error checking vision system state: {e}".format(e=e)
            )
            self._logger.error("[IMAGE] Request failed: {e}".format(e=e))

    def get_aruco_rpc(self, request, context):
        try:
            self._logger.debug(
                "[ARUCO] Request from client: {peer}".format(
                    peer=context.peer()
                )
            )
            self._logger.debug(
                "[ARUCO] Request details: {request}".format(request=request)
            )
            if not self.is_initialized or not self._vision_controller:
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                context.set_details("Vision system not initialized")
                self._logger.error(
                    "get_image_rpc called but vision system not initialized"
                )
                raise RuntimeError(
                    "Vision system not initialized. Call initialize() first."
                )

            aruco_array = self._vision_controller.detect_aruco()
            if aruco_array is None:
                context.set_code(grpc.StatusCode.UNAVAILABLE)
                context.set_details("ArUco detection failed")
                self._logger.warning("ArUco detection returned None")

            self._logger.debug(
                "[ARUCO] Detected ArUco markers: {array}".format(
                    array=aruco_array
                )
            )
            self._logger.debug(
                f"[ARUCO] Length of detected: {len(aruco_array)} markers"
            )

            return aruco_array.grpc
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(
                "Error checking vision system state: {e}".format(e=e)
            )
            self._logger.error("[ARUCO] Request failed: {e}".format(e=e))

    def get_qr_code_rpc(self, request, context):
        try:
            self._logger.debug(
                "[QR] Request from client: {peer}".format(peer=context.peer())
            )
            self._logger.debug(
                "[QR] Request details: {request}".format(request=request)
            )
            if not self.is_initialized or not self._vision_controller:
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                context.set_details("Vision system not initialized")
                self._logger.error(
                    "get_image_rpc called but vision system not initialized"
                )
                raise RuntimeError(
                    "Vision system not initialized. Call initialize() first."
                )

            qr_array = self._vision_controller.detect_qr_code()
            if qr_array is None:
                context.set_code(grpc.StatusCode.UNAVAILABLE)
                context.set_details("QR detection failed")
                self._logger.warning("QR detection returned None")
                return

            self._logger.debug(
                "[QR] Detected QR code: {array}".format(array=qr_array)
            )
            self._logger.debug(
                f"[QR] Length of detected: {len(qr_array)} codes"
            )

            return qr_array.grpc
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(
                "Error checking vision system state: {e}".format(e=e)
            )
            self._logger.error("[QR] Request failed: {e}".format(e=e))

    def get_blob_rpc(self, request, context):
        try:
            self._logger.debug(
                "[BLOB] Request from client: {peer}".format(
                    peer=context.peer()
                )
            )
            self._logger.debug(
                "[BLOB] Request details: {request}".format(request=request)
            )
            if not self.is_initialized or not self._vision_controller:
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                context.set_details("Vision system not initialized")
                self._logger.error(
                    "get_image_rpc called but vision system not initialized"
                )
                raise RuntimeError(
                    "Vision system not initialized. Call initialize() first."
                )

            blob_array = self._vision_controller.detect_blobs()
            if blob_array is None:
                context.set_code(grpc.StatusCode.UNAVAILABLE)
                context.set_details("Blob detection failed")
                self._logger.warning("Blob detection returned None")
                return

            self._logger.debug(
                "[BLOB] Detected blobs: {array}".format(array=blob_array)
            )
            self._logger.debug(
                f"[BLOB] Length of detected:{len(blob_array)} blobs"
            )

            return blob_array.grpc
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(
                "Error checking vision system state: {e}".format(e=e)
            )
            self._logger.error("[BLOB] Request failed: {e}".format(e=e))

    def release(self) -> None:
        with self._lock:
            if self._vision_controller:
                try:
                    self._vision_controller.release()
                    self._logger.info("VisionController released successfully")
                except Exception as e:
                    self._logger.error(
                        "Error releasing VisionController: {e}".format(e=e)
                    )
                finally:
                    self._vision_controller = None
            self._initialized = False
            self._logger.info("VisionController released")

    @property
    def is_initialized(self) -> bool:
        with self._lock:
            return self._initialized and self._vision_controller is not None

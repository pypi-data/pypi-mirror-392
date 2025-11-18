"""Camera configuration data class"""

from dataclasses import dataclass, field


@dataclass
class CameraConfig:
    """Configuration for the camera"""

    json: dict = field(
        default_factory=lambda: {
            "width": 640,
            "height": 480,
            "fps": 30,
            "url": "",
            "intrinsics": {
                "fx": 0.0,
                "fy": 0.0,
                "cx": 0.0,
                "cy": 0.0,
                "distortion": [0.0, 0.0, 0.0, 0.0, 0.0],
            },
            "auto_exposure": True,
            "brightness": 0,
            "contrast": 0,
            "saturation": 0,
            "position": {"x": 0.0, "y": 0.0, "z": 0.0},
            "rotation": [0.0, 0.0, 0.0],
        }
    )

    def __repr__(self) -> str:
        return (
            f"CameraConfig(width={self.json['width']}, "
            f"height={self.json['height']}, fps={self.json['fps']}, "
            f"url='{self.json['url']}')"
        )

    def sync(self, json: dict) -> None:
        """Update JSON representation with new values

        Args:
            json: A JSON dictionary with camera configuration
        """
        self.json.update(json)

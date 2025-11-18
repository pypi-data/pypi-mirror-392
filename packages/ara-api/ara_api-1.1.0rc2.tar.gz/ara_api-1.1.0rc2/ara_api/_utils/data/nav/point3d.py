"""3D Point with position and yaw"""

from dataclasses import dataclass, field

from ara_api._utils.data.nav.vector3 import Vector3


@dataclass
class Point3D:
    position: Vector3 = field(default_factory=lambda: Vector3())
    yaw: float = 0.0

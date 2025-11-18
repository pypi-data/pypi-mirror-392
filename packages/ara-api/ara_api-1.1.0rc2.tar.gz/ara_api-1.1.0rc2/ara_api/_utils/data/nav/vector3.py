"""3D Vector data class"""

from dataclasses import dataclass, field

import numpy as np

from ara_api._utils.communication import vector3


@dataclass
class Vector3:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    grpc: vector3 = field(default_factory=lambda: vector3(), init=False)

    def __post_init__(self) -> None:
        self.grpc.x = self.x
        self.grpc.y = self.y
        self.grpc.z = self.z

    def __repr__(self):
        return "Vector3(x={x}, y={y}, z={z})".format(
            x=self.x, y=self.y, z=self.z
        )

    def __add__(self, other) -> "Vector3":
        if isinstance(other, Vector3):
            return Vector3(
                x=self.x + other.x,
                y=self.y + other.y,
                z=self.z + other.z,
            )
        raise NotImplementedError(
            "Addition with non-Vector3 object is not supported"
        )

    def __sub__(self, other) -> "Vector3":
        if isinstance(other, Vector3):
            return Vector3(
                x=self.x - other.x,
                y=self.y - other.y,
                z=self.z - other.z,
            )
        raise NotImplementedError(
            "Subtraction with non-Vector3 object is not supported"
        )

    def __mul__(self, scalar) -> "Vector3":
        if isinstance(scalar, float) or isinstance(scalar, int):
            return Vector3(
                x=self.x * scalar,
                y=self.y * scalar,
                z=self.z * scalar,
            )
        raise NotImplementedError(
            "Multiplication with non-float or non-int object is not supported"
        )

    def __rmul__(self, scalar) -> "Vector3":
        return self.__mul__(scalar)

    def __matmul__(self, other) -> float:
        if isinstance(other, Vector3):
            return self.x * other.x + self.y * other.y + self.z * other.z
        raise NotImplementedError(
            "Dot product with non-Vector3 object is not supported"
        )

    def __rmatmul__(self, other) -> float:
        return self.__matmul__(other)

    @property
    def as_grpc(self) -> vector3:
        return self.grpc

    @property
    def as_numpy(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z])

    @property
    def magnitude(self) -> float:
        return float(np.linalg.norm([self.x, self.y, self.z]))

    def cross(self, other) -> "Vector3":
        if isinstance(other, Vector3):
            return Vector3(
                x=self.y * other.z - self.z * other.y,
                y=self.z * other.x - self.x * other.z,
                z=self.x * other.y - self.y * other.x,
            )
        else:
            raise NotImplementedError(
                "Cross product with non-Vector3 object is not supported"
            )

    def from_grpc(self, grpc: vector3) -> None:
        self.x = grpc.x
        self.y = grpc.y
        self.z = grpc.z

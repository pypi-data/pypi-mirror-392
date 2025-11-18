"""Rotation data class with support for quaternions, euler angles, rotation matrices"""

from dataclasses import dataclass, field
from typing import Any, NoReturn, Tuple, Union

import numpy as np
from scipy.spatial.transform import Rotation as R


@dataclass
class Rotation:
    data: Union[
        Tuple[float, float, float, float],  # quaternion
        Tuple[int, int, int],  # euler in degrees
        Tuple[float, float, float],  # rotvec in radians
        Tuple[
            Tuple[float, float, float],
            Tuple[float, float, float],
            Tuple[float, float, float],
        ],  # rotation matrix
        R,  # scipy Rotation object
    ] = field(default_factory=lambda: np.array([0, 0, 0], dtype=np.int64))
    rotation: Any = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.data, R):
            data = np.array(self.data)
            if data.ndim == 2:
                self.rotation = R.from_matrix(data)
            elif data.ndim == 1:
                if data.size == 4:
                    self.rotation = R.from_quat(data)
                elif data.size == 3:
                    if data.dtype == np.int64:
                        self.rotation = R.from_euler("xyz", data, degrees=True)
                    elif data.dtype == np.float64:
                        self.rotation = R.from_rotvec(data)
                    else:
                        raise Exception("Invalid data type inside data")
                else:
                    raise Exception("Invalid size of data")
            else:
                raise Exception("Invalid data shape")
        elif isinstance(self.data, R):
            self.rotation = self.data
        else:
            raise Exception("Invalid data type")

    def __repr__(self):
        return (
            "Rotation(euler={euler}, quaternion={quat}, rotvec={rotvec},"
            " matrix={matrix})".format(
                euler=self.as_euler,
                quat=self.as_quat,
                rotvec=self.as_rotvec,
                matrix=self.as_matrix,
            )
        )

    def __truediv__(self, other) -> NoReturn:
        raise NotImplementedError(
            "Division is not supported for Rotation objects"
        )

    def __add__(self, other) -> NoReturn:
        raise NotImplementedError(
            "Addition is not supported for Rotation objects"
        )

    def __sub__(self, other) -> "Rotation":
        if isinstance(other, Rotation):
            return Rotation(self.rotation * other.rotation.inv())
        else:
            return Rotation(self.rotation * Rotation(other).inv())

    def __mul__(self, other) -> "Rotation":
        if isinstance(other, Rotation):
            return Rotation(self.rotation * other.rotation)
        else:
            return Rotation(self.rotation * Rotation(other))

    def __pow__(self, other) -> "Rotation":
        return Rotation(self.rotation**other)

    def __invert__(self) -> "Rotation":
        return Rotation(self.rotation.inv())

    @property
    def as_quat(self) -> np.ndarray:
        return self.rotation.as_quat()

    @property
    def as_euler(self) -> np.ndarray:
        return self.rotation.as_euler("xyz", degrees=True)

    @property
    def as_matrix(self) -> np.ndarray:
        return self.rotation.as_matrix()

    @property
    def as_rotvec(self) -> np.ndarray:
        return self.rotation.as_rotvec()

    def angle_to(self, other: "Rotation") -> float:
        diff = self.rotation.inv() * other.rotation
        return diff.magnitude()

    # Method for creating a Rotation object from two directions
    @classmethod
    def from_two_vectors(cls, v1: np.ndarray, v2: np.ndarray) -> "Rotation":
        v1 = np.array(v1) / np.linalg.norm(v1)
        v2 = np.array(v2) / np.linalg.norm(v2)

        if np.allclose(v1, v2):
            return cls([0, 0, 0], dtype=np.int64)

        if np.allclose(v1, -v2):
            perp = np.array([1, 0, 0])
            if np.allclose(np.abs(np.dot(perp, v1)), 1.0):
                perp = np.array([0, 1, 0])
            perp = perp - np.dot(perp, v1) * v1
            perp = perp / np.linalg.norm(perp)

            return cls(perp * np.pi)

        axis = np.cross(v1, v2)
        axis = axis / np.linalg.norm(axis)
        angle = np.arccos(np.clip(np.dot(v1, v2), -1.0, 1.0))

        return cls(axis * angle)

    @classmethod
    def from_two_position(cls, p1: np.ndarray, p2: np.ndarray) -> "Rotation":
        return Rotation.from_two_vectors(
            [1, 0, 0], (p1 - p2) / np.linalg.norm(p1 - p2)
        )

    def apply(self, vector):
        return self.rotation.apply(vector)

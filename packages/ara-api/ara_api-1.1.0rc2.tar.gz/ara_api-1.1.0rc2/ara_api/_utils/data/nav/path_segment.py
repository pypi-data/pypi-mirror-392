"""Path segment data class representing trajectory segment"""

from dataclasses import dataclass, field

from ara_api._utils.data.nav.rotation import Rotation
from ara_api._utils.data.nav.vector3 import Vector3


@dataclass
class PathSegment:
    start: Vector3 = field(default_factory=lambda: Vector3())
    end: Vector3 = field(default_factory=lambda: Vector3())

    start_heading: Rotation = field(
        default_factory=lambda: Rotation([0, 0, 0])
    )
    end_heading: Rotation = field(default_factory=lambda: Rotation([0, 0, 0]))

    metadata: dict = field(default_factory=lambda: {})

    def __post_init__(self) -> None:
        if not isinstance(self.start, Vector3):
            if self.start is not None and isinstance(self.start, tuple):
                self.start = Vector3(
                    x=self.start[0], y=self.start[1], z=self.start[2]
                )
            else:
                raise Exception("Invalid start data")

        if not isinstance(self.end, Vector3):
            if self.end is not None and isinstance(self.end, tuple):
                self.end = Vector3(x=self.end[0], y=self.end[1], z=self.end[2])
            else:
                raise Exception("Invalid end data")

        if not isinstance(self.start_heading, Rotation):
            if self.start_heading is not None and isinstance(
                self.start_heading, tuple
            ):
                self.start_heading = Rotation(self.start_heading)
            else:
                raise Exception("Invalid start_heading data")

        if not isinstance(self.end_heading, Rotation):
            if self.end_heading is not None and isinstance(
                self.end_heading, tuple
            ):
                self.end_heading = Rotation(self.end_heading)
            else:
                raise Exception("Invalid end_heading data")

    def __repr__(self):
        return (
            "PathSegment(start={start}, end={end}, "
            "start_heading={start_heading}, end_heading={end_heading})"
        ).format(
            start=self.start,
            end=self.end,
            start_heading=self.start_heading,
            end_heading=self.end_heading,
        )

    @property
    def length(self):
        return (self.end - self.start).magnitude

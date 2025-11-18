"""Path data class representing complete trajectory"""

from dataclasses import dataclass, field
from typing import List

from ara_api._utils.data.nav.path_segment import PathSegment
from ara_api._utils.data.nav.vector3 import Vector3


@dataclass
class Path:
    segments: List[PathSegment] = field(default_factory=lambda: [])
    is_cyclic: bool = False

    @property
    def length(self):
        length = 0
        for segment in self.segments:
            length += segment.length
        return length

    @property
    def start(self) -> Vector3:
        return self.segments[0].start

    @property
    def end(self) -> Vector3:
        return self.segments[-1].end

    def __repr__(self):
        return (
            "Path(segments={segments}, is_cyclic={is_cyclic}, start={start}"
            ", end={end}, lenght={lenght})".format(
                segments=self.segments,
                is_cyclic=self.is_cyclic,
                start=self.start,
                end=self.end,
                lenght=self.length,
            )
        )

    def add_segment(self, segment: PathSegment):
        self.segments.append(segment)

    def insert_segment(self, index: int, segment: PathSegment):
        self.segments.insert(index, segment)

    def remove_segment(self, index: int):
        self.segments.pop(index)

    def clear(self):
        self.segments.clear()

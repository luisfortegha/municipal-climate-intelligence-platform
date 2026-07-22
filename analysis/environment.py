from dataclasses import dataclass
from shapely.geometry import box


@dataclass(frozen=True)
class StudyArea:
    name: str
    min_lon: float
    min_lat: float
    max_lon: float
    max_lat: float

    @property
    def bbox(self):
        return (
            self.min_lon,
            self.min_lat,
            self.max_lon,
            self.max_lat,
        )

    @property
    def bounds(self):
        return self.bbox

    @property
    def polygon(self):
        return box(*self.bbox)

    @property
    def center(self):
        return (
            (self.min_lat + self.max_lat) / 2,
            (self.min_lon + self.max_lon) / 2,
        )

    @classmethod
    def from_bbox(
        cls,
        name: str,
        west: float,
        south: float,
        east: float,
        north: float,
    ):
        return cls(
            name=name,
            min_lon=west,
            min_lat=south,
            max_lon=east,
            max_lat=north,
        )
    
NASHVILLE = StudyArea(
    name="Nashville-Davidson County",
    min_lon=-87.07,
    min_lat=35.90,
    max_lon=-86.56,
    max_lat=36.42,
)


STUDY_AREAS = {
    "Nashville-Davidson": StudyArea(
        name="Nashville-Davidson",
        min_lon=-87.07,
        min_lat=35.90,
        max_lon=-86.56,
        max_lat=36.42,
    ),

    "Franklin": StudyArea(
        name="Franklin",
        min_lon=-86.92,
        min_lat=35.87,
        max_lon=-86.78,
        max_lat=36.02,
    ),

    "Murfreesboro": StudyArea(
        name="Murfreesboro",
        min_lon=-86.47,
        min_lat=35.75,
        max_lon=-86.28,
        max_lat=35.95,
    ),

    "Clarksville": StudyArea(
        name="Clarksville",
        min_lon=-87.48,
        min_lat=36.45,
        max_lon=-87.18,
        max_lat=36.67,
    ),
}

DEFAULT_STUDY_AREA = STUDY_AREAS["Nashville-Davidson"]
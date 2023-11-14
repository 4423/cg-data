import dataclasses


@dataclasses.dataclass
class Song:
    title: str
    artists: list[str]
    unit_name: str | None = None
    is_covered: bool = False
    original_artist: str | None = None

    def asdict(self):
        return dataclasses.asdict(self)

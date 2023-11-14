import dataclasses


@dataclasses.dataclass
class Character:
    name: str
    actor: str

    def asdict(self):
        return dataclasses.asdict(self)

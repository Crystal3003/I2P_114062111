class NavigatePoint:
    def __init__(self, x, y, name):
        self.x = x
        self.y = y
        self.name = name
    @classmethod
    def from_dict(cls, data: dict) -> "NavigatePoint":
        x = data.get("x")
        y = data.get("y")
        name = data.get("name")
        return cls(x, y, name)
    def to_dict(self) -> dict[str, object]:
        return {
            "x": self.x,
            "y": self.y,
            "name": self.name
        }
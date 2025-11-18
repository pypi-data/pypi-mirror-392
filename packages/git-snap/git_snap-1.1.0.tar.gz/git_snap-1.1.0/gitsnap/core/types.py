from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Snapshot:
    """Represents a git snapshot."""
    internal_name: str
    tag: str
    date: datetime
    message: str
    type: str = field(default="none")
    description: str = field(default="")


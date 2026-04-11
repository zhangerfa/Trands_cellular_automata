from dataclasses import dataclass
from typing import Optional


@dataclass
class Lane:
    sections: dict[str, int]  # {section_type: length}

    @property
    def length(self) -> int:
        return sum(self.sections.values())

    def section_at(self, x: int) -> Optional[str]:
        pos = 0
        for section_type, section_length in self.sections.items():
            pos += section_length
            if x < pos:
                return section_type
        return None

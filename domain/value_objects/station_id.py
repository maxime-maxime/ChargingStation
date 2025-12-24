from dataclasses import dataclass


@dataclass(frozen=True)
class StationId:
    """Value object representing a charging station identifier"""
    value: str
    
    def __post_init__(self):
        # Validation rules
        if not self.value or not self.value.strip():
            raise ValueError("Station ID cannot be empty")
        
        if len(self.value) > 50:
            raise ValueError("Station ID too long (max 50 characters)")
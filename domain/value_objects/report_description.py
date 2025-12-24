from dataclasses import dataclass


@dataclass(frozen=True)
class ReportDescription:
    """Value object for malfunction report description"""
    value: str
    
    def __post_init__(self):
        # Validation rules
        if not self.value or not self.value.strip():
            raise ValueError("Description cannot be empty")
        
        if len(self.value) < 10:
            raise ValueError("Description too short (minimum 10 characters)")
        
        if len(self.value) > 500:
            raise ValueError("Description too long (maximum 500 characters)")
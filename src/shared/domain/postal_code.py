class PostalCode:
    def __init__(self, value: str):
        self._validate(value)
        self.value = value

    def _validate(self, value: str):

        if len(value) != 5:
            raise ValueError(f"Postal code must be 5 digits, got {len(value)}")

        if not value.isdigit():
            raise ValueError(f"Postal code must contain only digits: {value}")

        if not value.startswith('1'):
            raise ValueError(f"Not a valid Berlin postal code: {value}")

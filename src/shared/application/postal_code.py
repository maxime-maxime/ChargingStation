import pandas as pd

class PostalCode:
    # On charge l'index de référence une seule fois au niveau de la classe
    _valid_codes = None

    def __init__(self, value: str):
        self._validate(value)
        self.value = value

    @classmethod
    def _load_data(cls):
        if cls._valid_codes is None:
            df = pd.read_csv('../infrastructure/datasets/geodata_berlin_plz.csv')
            cls._valid_codes = set(df['PLZ'].astype(str).values)

    def _validate(self, value: str):
        if len(value) != 5:
            raise ValueError(f"Postal code must be 5 digits, got {len(value)}")
        if not value.isdigit():
            raise ValueError(f"Postal code must contain only digits: {value}")
        if not value.startswith('1'):
            raise ValueError(f"Not a valid Berlin postal code: {value}")

        # 2. Validation par rapport au CSV (plus coûteuse)
        self._load_data()
        if value not in self._valid_codes:
            raise ValueError(f"Postal code is not in the dataSet: {value}")
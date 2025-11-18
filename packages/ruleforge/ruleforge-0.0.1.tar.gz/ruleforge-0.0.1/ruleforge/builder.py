class ColumnPolicyBuilder:
    def __init__(self, name: str):
        self.name = name
        self.scope = "column"
        self.validators = []

    def add_validator(self, validator):
        self.validators.append(validator)
        return self


class RowPolicyBuilder:
    def __init__(self):
        self.scope = "row"
        self.validators = []

    def add_validator(self, validator):
        self.validators.append(validator)
        return self

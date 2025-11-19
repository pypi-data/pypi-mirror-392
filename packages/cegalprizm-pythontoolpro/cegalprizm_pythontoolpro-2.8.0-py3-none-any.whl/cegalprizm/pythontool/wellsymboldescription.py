# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.




class WellSymbolDescription:
    def __init__(self, id: int, name: str, description: str):
        self._id = id
        self._name = name
        self._description = description

    @property
    def id(self) -> int:
        """The ID of the well symbol description"""
        return self._id

    @property
    def name(self) -> str:
        """The (unique) name of the well symbol description"""
        return self._name

    @property
    def description(self) -> str:
        """The description of the well symbol description"""
        return self._description

    def __str__(self) -> str:
        return f"WellSymbolDescription(({self._id}) {self._description})"

    def __repr__(self) -> str:
        return f"WellSymbolDescription(({self._id}) {self._description})"
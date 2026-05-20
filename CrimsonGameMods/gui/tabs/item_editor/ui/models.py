
from .dmm_types import ItemInfo


class ItemEditorInfo:
    def __init__(self, data: list[ItemInfo] = []):
        self._data = data

    def details(self, idx):
        return ItemEditorInfoDetails(self._data[idx])

class ItemEditorInfoDetails:
    def __init__(self, data: ItemInfo = {}):
        self._data = data
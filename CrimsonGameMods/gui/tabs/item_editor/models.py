from .dmm_types import ItemInfo
from collections import UserDict, UserList
import copy
import json
import logging

log = logging.getLogger(__name__)


class ItemEditorInfo:
    def __init__(self, data: list[ItemInfo] = []):
        self._data = data

    def __len__(self):
        return len(self._data)

    def details(self, idx):
        if idx < 0 or idx > len(self._data):
            raise IndexError("Index not in range!")

        return ItemEditorInfoDetails(self._data[idx])


class ItemEditorInfoDetails:
    EDITABLE_ENTRIES = [
        "cooltime",
        "docking_child_data",
        "drop_default_data",
        "enchant_data_list",
        "equip_passive_skill_list",
        "gimmick_info",
        "gimmick_visual_prefab_data_list",
        "is_dyeable",
        "item_charge_type",
        "item_tier",
        "max_charged_useable_count",
        "max_endurance",
        "max_stack_count",
        "price_list",
    ]

    def __init__(self, data: ItemInfo = {}):
        # self._item_info = data
        self._data = data
        self._history = []

    def __getitem__(self, key):
        return self._data[key]

    def items(self):
        return self._data.items()

    def editable(self):
        return (
            [(key, self._data.get(key, None)) for key in self.EDITABLE_ENTRIES]
            if self._data
            else []
        )


NOT_FOUND = object()


class HistoryRegistry:
    """Manages transactional logging and maps proxy references across data trees."""

    def __init__(self):
        self.history = []
        self.track = True

    def log(self, container, action, key, old_value):
        if self.track:
            self.history.append((container, action, key, old_value))

    def undo(self, root):
        if not self.history:
            print("No history to undo.")
            return

        self.track = False
        try:
            container, action, key, old_value = self.history.pop()

            if isinstance(container, ReversibleDict):
                if action == "SET":
                    if old_value is NOT_FOUND:
                        if key in container.data:
                            del container.data[key]
                    else:
                        container.data[key] = container._wrap(key, old_value)
                elif action == "DEL":
                    container.data[key] = container._wrap(key, old_value)

            elif isinstance(container, ReversibleList):
                if action == "SET":
                    container.data[key] = container._wrap(key, old_value)
                elif action == "APPEND":
                    container.data.pop()
                elif action == "POP":
                    container.data.insert(key, container._wrap(key, old_value))
        finally:
            self.track = True


class ReversibleList(UserList):
    def __init__(self, initlist=None, registry=None):
        super().__init__()
        self._registry = (
            registry if registry is not None else HistoryRegistry()
        )
        if initlist is not None:
            # Populating raw items silently first
            for item in initlist:
                self.data.append(self._wrap(len(self.data), item))

    def _wrap(self, index, value):
        if isinstance(value, dict) and not isinstance(value, ReversibleDict):
            return ReversibleDict(value, registry=self._registry)
        if isinstance(value, list) and not isinstance(value, ReversibleList):
            return ReversibleList(value, registry=self._registry)
        return value

    def _unwrap(self, val):
        return (
            val.data
            if isinstance(val, (ReversibleDict, ReversibleList))
            else val
        )

    def __setitem__(self, index, value):
        old_val = self.data[index]
        value = self._wrap(index, value)
        self._registry.log(
            self, "SET", index, copy.deepcopy(self._unwrap(old_val))
        )
        super().__setitem__(index, value)

    def append(self, value):
        idx = len(self.data)
        value = self._wrap(idx, value)
        self._registry.log(self, "APPEND", idx, None)
        super().append(value)

    def pop(self, index=-1):
        idx = index if index >= 0 else len(self.data) + index
        old_val = self.data[idx]
        self._registry.log(
            self, "POP", idx, copy.deepcopy(self._unwrap(old_val))
        )
        return super().pop(idx)


class ReversibleDict(UserDict):
    def __init__(self, dict_data=None, registry=None):
        self.data = {}
        self._registry = (
            registry if registry is not None else HistoryRegistry()
        )
        if dict_data:
            for k, v in dict_data.items():
                self.data[k] = self._wrap(k, v)

    def _wrap(self, key, value):
        if isinstance(value, dict) and not isinstance(value, ReversibleDict):
            return ReversibleDict(value, registry=self._registry)
        if isinstance(value, list) and not isinstance(value, ReversibleList):
            return ReversibleList(value, registry=self._registry)
        return value

    def _unwrap(self, val):
        return (
            val.data
            if isinstance(val, (ReversibleDict, ReversibleList))
            else val
        )

    def __setitem__(self, key, value):
        old_value = self.data.get(key, NOT_FOUND)
        value = self._wrap(key, value)
        self._registry.log(
            self, "SET", key, copy.deepcopy(self._unwrap(old_value))
        )
        super().__setitem__(key, value)

    def __delitem__(self, key):
        if key not in self.data:
            raise KeyError(key)
        old_value = self.data[key]
        self._registry.log(
            self, "DEL", key, copy.deepcopy(self._unwrap(old_value))
        )
        super().__delitem__(key)

    def undo(self):
        """Rolls back the global state using explicit container instance references."""
        self._registry.undo(self)


# # Initialize data with nested structural variations
# user_data = ReversibleDict({
#     "username": "coder123",
#     "tasks": [
#         {"id": 1, "status": "pending"},
#         {"id": 2, "status": "completed"}
#     ]
# })

# print("Original Object:")
# print(user_data)

# # Mutation 1: Update an attribute inside a list item
# user_data['tasks'][0]['status'] = 'in_progress'

# # Mutation 2: Append a new element to the list
# user_data['tasks'].append({"id": 3, "status": "backlog"})

# print("\nMutated Object:")
# print(user_data)
# # {'username': 'coder123', 'tasks': [{'id': 1, 'status': 'in_progress'}, {'id': 2, 'status': 'completed'}, {'id': 3, 'status': 'backlog'}]}

# # Undo Mutation 2 (The Append)
# user_data.undo()
# print("\nAfter Undo 1 (Removes appended item):")
# print(user_data['tasks'])
# # [{'id': 1, 'status': 'in_progress'}, {'id': 2, 'status': 'completed'}]

# # Undo Mutation 1 (The Inner dict change)
# user_data.undo()
# print("\nAfter Undo 2 (Reverts status modification):")
# print(user_data['tasks'])
# # [{'id': 1, 'status': 'pending'}, {'id': 2, 'status': 'completed'}]

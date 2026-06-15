from typing import Any, List, Union
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from PySide6.QtWidgets import QTableView, QComboBox, QStyledItemDelegate, QApplication, QWidget, QStyleOptionViewItem
import sys

class MyModel(QAbstractTableModel):
    def __init__(self, data: List[List[str]]) -> None:
        super().__init__()
        self._data: List[List[str]] = data

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._data) if self._data else 0

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Union[str, None]:
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            return self._data[index.row()][index.column()]
        return None

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.ItemDataRole.EditRole) -> bool:
        if role == Qt.ItemDataRole.EditRole:
            self._data[index.row()][index.column()] = str(value)
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable

# 1. Setup Application, Data Model, and View
app: QApplication = QApplication(sys.argv)
data: List[List[str]] = [["Task 1", "Pending"], ["Task 2", "In Progress"], ["Task 3", "Done"]]
model: MyModel = MyModel(data)

view: QTableView = QTableView()
view.setModel(model)

# 2. Instantiate a standard delegate
inline_delegate: QStyledItemDelegate = QStyledItemDelegate(view)

# 3. Define inline methods with strict type definitions
def custom_create_editor(parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> QComboBox:
    combo: QComboBox = QComboBox(parent)
    combo.addItems(["Pending", "In Progress", "Done"])
    return combo

def custom_set_editor_data(editor: QComboBox, index: QModelIndex) -> None:
    current_text: Any = index.data(Qt.ItemDataRole.EditRole)
    editor.setCurrentText(str(current_text))

def custom_set_model_data(editor: QComboBox, model: QAbstractTableModel, index: QModelIndex) -> None:
    chosen_text: str = editor.currentText()
    model.setData(index, chosen_text, Qt.ItemDataRole.EditRole)

# 4. Bind the monkey-patched methods to the delegate instance
inline_delegate.createEditor = custom_create_editor  # type: ignore[assignment]
inline_delegate.setEditorData = custom_set_editor_data  # type: ignore[assignment]
inline_delegate.setModelData = custom_set_model_data  # type: ignore[assignment]

# 5. Target only Column 1
view.setItemDelegateForColumn(1, inline_delegate)

view.resize(300, 150)
view.show()
sys.exit(app.exec())


from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from PySide6.QtGui import QColor

class CustomTableModel(QAbstractTableModel):
    def __init__(self, data_matrix):
        super().__init__()
        self._data = data_matrix

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._data[0]) if self._data else 0

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        # Fetch raw value from internal storage
        raw_value = self._data[index.row()][index.column()]

        # 1. Text to display in the cell
        if role == Qt.ItemDataRole.DisplayRole:
            return str(raw_value)

        # 2. Text to show inside the editor widget when editing
        elif role == Qt.ItemDataRole.EditRole:
            return raw_value

        # 3. Dynamic background colors based on value
        elif role == Qt.ItemDataRole.BackgroundRole:
            if isinstance(raw_value, (int, float)) and raw_value < 0:
                return QColor("pink")  # Highlight negative numbers

        # 4. Interactive tooltips
        elif role == Qt.ItemDataRole.ToolTipRole:
            return f"Row {index.row()}, Col {index.column()} raw data: {raw_value}"

        # Return None for any roles your model doesn't explicitly support
        return None

from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex, QSize
from PySide6.QtGui import QColor, QFont, QIcon, QBrush

class ExhaustiveDataModel(QAbstractTableModel):
    def __init__(self, dataset):
        super().__init__()
        # Mock internal data: list of dicts representing data rows
        self._data = dataset 

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._data[0]) if self._data else 0

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        # Always validate the incoming index first
        if not index.isValid():
            return None
            
        row = index.row()
        col = index.column()
        
        # Out-of-bounds safety check
        if row >= len(self._data) or col >= len(self._data[0]):
            return None

        # Extract target item raw information 
        cell_info = self._data[row][col] 

        # --- 1. CORE DATA ROLES ---
        if role == Qt.ItemDataRole.DisplayRole:
            # What the user sees rendered as a text string
            return str(cell_info.get("value", ""))

        elif role == Qt.ItemDataRole.EditRole:
            # The raw underlying value passed to an editor widget (e.g., QLineEdit, QSpinBox)
            return cell_info.get("value")

        elif role == Qt.ItemDataRole.CheckStateRole:
            # Controls a checkbox. Must return Qt.CheckState enum or None if no checkbox
            if cell_info.get("has_checkbox"):
                return Qt.CheckState.Checked if cell_info.get("checked") else Qt.CheckState.Unchecked
            return None


        # --- 2. VISUAL STYLING & APPEARANCE ROLES ---
        elif role == Qt.ItemDataRole.ForegroundRole:
            # Text color. Returns a QColor or a QBrush
            if cell_info.get("is_critical"):
                return QColor(Qt.GlobalColor.red)
            return QColor(Qt.GlobalColor.black)

        elif role == Qt.ItemDataRole.BackgroundRole:
            # Cell background color. Returns a QColor or a QBrush
            if row % 2 == 0:
                return QColor("#f0f0f0") # Alternating row color
            return QColor(Qt.GlobalColor.white)

        elif role == Qt.ItemDataRole.FontRole:
            # Custom font typography for this cell. Returns a QFont
            font = QFont()
            if col == 0: 
                font.setBold(True) # Bold the primary identifier column
            return font

        elif role == Qt.ItemDataRole.TextAlignmentRole:
            # How the text lines up. Returns a Qt.AlignmentFlag combination
            if isinstance(cell_info.get("value"), (int, float)):
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter

        elif role == Qt.ItemDataRole.DecorationRole:
            # An icon, pixmap, or small color swatch rendered next to text. Returns QIcon/QPixmap/QColor
            if cell_info.get("is_complete"):
                return QIcon("icons/check.png")
            return None


        # --- 3. METADATA & HELPER ROLES ---
        elif role == Qt.ItemDataRole.ToolTipRole:
            # Text popping up on mouse hover
            return f"Database ID: {cell_info.get('id')}\nStatus: {cell_info.get('status')}"

        elif role == Qt.ItemDataRole.StatusTipRole:
            # Text sent to the QMainWindow status bar on hover
            return f"Editing item index: {row}, {col}"

        elif role == Qt.ItemDataRole.WhatsThisRole:
            # Text shown when utilizing the "What's This?" help mode help button
            return "This cell represents the real-time calculated financial profit margin."


        # --- 4. LAYOUT & HINT ROLES ---
        elif role == Qt.ItemDataRole.SizeHintRole:
            # Tells the view preferred dimensions for this specific cell. Returns a QSize
            return QSize(120, 35)


        # --- 5. CUSTOM USER ROLES (Passed explicitly by backend logic) ---
        elif role == Qt.ItemDataRole.UserRole:
            # Custom identifier role offset
            return cell_info.get("id")

        elif role == (Qt.ItemDataRole.UserRole + 1):
            # Pass back the entire raw Python dictionary object
            return cell_info


        # --- FALLBACK ---
        # Crucial: return None for any role you do not explicitly handle.
        # This tells Qt to fall back to its internal view style engine defaults.
        return None

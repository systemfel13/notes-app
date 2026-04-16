import os
import sys

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QTextEdit, QLineEdit, QPushButton,
    QMessageBox, QLabel, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QFontDatabase, QIcon, QPalette, QColor, QTextCharFormat, QTextCursor

import database

class NotesApp(QMainWindow):
    def __init__(self):
        super().__init__()
        database.init_db()
        self.current_note_id = None
        self._dirty = False
        self._loading_note = False
        self._init_ui()
        self._load_notes()

    def _init_ui(self):
        self.setWindowTitle("Notes")
        self.setMinimumSize(900, 560)
        self.resize(1060, 640)

        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Top section: sidebar header + buttons/title 
        top_section = QWidget()
        top_section_layout = QHBoxLayout(top_section)
        top_section_layout.setContentsMargins(0, 0, 0, 0)
        top_section_layout.setSpacing(0)

        sidebar_header = QFrame()
        sidebar_header.setObjectName("sidebarHeader")
        sidebar_header.setFixedWidth(260)
        top_section_layout.addWidget(sidebar_header)

        header_right = QWidget()
        header_right.setObjectName("editorArea")
        header_right_layout = QVBoxLayout(header_right)
        header_right_layout.setContentsMargins(0, 0, 0, 0)
        header_right_layout.setSpacing(0)

        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        top_bar.setFixedHeight(52)
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(16, 0, 16, 0)

        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        top_bar_layout.addWidget(self.status_label)

        top_bar_layout.addStretch()

        self.btn_bold = QPushButton("B")
        self.btn_bold.setObjectName("btnBold")
        self.btn_bold.setFixedSize(32, 32)
        self.btn_bold.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_bold.setCheckable(True)
        self.btn_bold.clicked.connect(self._toggle_bold)
        top_bar_layout.addWidget(self.btn_bold)

        self.btn_underline = QPushButton("U")
        self.btn_underline.setObjectName("btnUnderline")
        self.btn_underline.setFixedSize(32, 32)
        self.btn_underline.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_underline.setCheckable(True)
        self.btn_underline.clicked.connect(self._toggle_underline)
        top_bar_layout.addWidget(self.btn_underline)

        self.btn_new = QPushButton("  New Note")
        self.btn_new.setObjectName("btnNew")
        self.btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new.setFixedHeight(34)
        self.btn_new.clicked.connect(self._new_note)
        top_bar_layout.addWidget(self.btn_new)

        header_right_layout.addWidget(top_bar)

        self.title_edit = QLineEdit()
        self.title_edit.setObjectName("titleEdit")
        self.title_edit.setPlaceholderText("Title...")
        self.title_edit.textChanged.connect(self._mark_dirty)
        header_right_layout.addWidget(self.title_edit)

        top_section_layout.addWidget(header_right, 1)
        root_layout.addWidget(top_section)

        # Full-width separator line between the top and bottom sections
        title_separator = QFrame()
        title_separator.setObjectName("titleSeparator")
        title_separator.setFixedHeight(1)
        root_layout.addWidget(title_separator)

        # Bottom section: note list + editor 
        bottom_section = QWidget()
        bottom_section_layout = QHBoxLayout(bottom_section)
        bottom_section_layout.setContentsMargins(0, 0, 0, 0)
        bottom_section_layout.setSpacing(0)

        self.note_list = QListWidget()
        self.note_list.setObjectName("noteList")
        self.note_list.setFixedWidth(260)
        # Let long titles wrap to multiple lines instead of being cut off
        self.note_list.setWordWrap(True)
        self.note_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.note_list.currentItemChanged.connect(self._on_note_selected)
        bottom_section_layout.addWidget(self.note_list)

        editor_bottom = QWidget()
        editor_bottom.setObjectName("editorArea")
        editor_bottom_layout = QVBoxLayout(editor_bottom)
        editor_bottom_layout.setContentsMargins(0, 0, 0, 0)
        editor_bottom_layout.setSpacing(0)

        self.text_edit = QTextEdit()
        self.text_edit.setObjectName("textEdit")
        self.text_edit.setPlaceholderText("Write your note here...")
        self.text_edit.setFont(QFont("EB Garamond", 14))
        self.text_edit.cursorPositionChanged.connect(self._update_format_buttons)
        palette = self.text_edit.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor("#fff0f5"))
        self.text_edit.setPalette(palette)
        self.text_edit.textChanged.connect(self._mark_dirty)
        editor_bottom_layout.addWidget(self.text_edit)

        action_bar = QFrame()
        action_bar.setObjectName("actionBar")
        action_bar.setFixedHeight(52)
        action_bar_layout = QHBoxLayout(action_bar)
        action_bar_layout.setContentsMargins(16, 0, 16, 0)

        self.btn_delete = QPushButton("Delete")
        self.btn_delete.setObjectName("btnDelete")
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.setFixedHeight(34)
        self.btn_delete.clicked.connect(self._delete_note)
        action_bar_layout.addWidget(self.btn_delete)

        action_bar_layout.addStretch()

        self.btn_save = QPushButton("Save")
        self.btn_save.setObjectName("btnSave")
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setFixedHeight(34)
        self.btn_save.clicked.connect(self._save_note)
        action_bar_layout.addWidget(self.btn_save)

        editor_bottom_layout.addWidget(action_bar)

        bottom_section_layout.addWidget(editor_bottom, 1)
        root_layout.addWidget(bottom_section, 1)

        self._apply_styles()
        self._set_editor_enabled(False)

    def _apply_styles(self):
        self.setStyleSheet("""
            QMainWindow { background: #fff0f5; }

            #sidebarHeader {
                background: #f5b8cb;
            }
            #noteList {
                background: #f5b8cb;
                color: #4a2030;
                border: none;
                font-size: 14pt;
                font-weight: 400;
                padding: 4px 0;
                outline: none;
            }
            #noteList::item {
                padding: 10px 16px;
                border-bottom: 1px solid #eea8bc;
            }
            #noteList::item:selected {
                background: #e8a0b5;
                color: #ffffff;
            }
            #noteList::item:hover:!selected {
                background: #f0adc2;
            }

            #editorArea {
                background: #fff0f5;
            }
            #topBar {
                background: #fff0f5;
            }
            #statusLabel {
                color: #8e8e93;
                font-size: 12px;
            }
            #btnNew {
                background: #e8a0b5;
                color: #000000;
                border: none;
                border-radius: 6px;
                padding: 0 18px;
                font-size: 14pt;
                font-weight: 400;
            }
            #btnNew:hover { background: #df90a8; }
            #btnNew:pressed { background: #d6809b; }

            #titleEdit {
                border: none;
                background: #fff0f5;
                padding: 4px 20px;
                font-size: 28px;
                font-weight: 600;
                color: #1c1c1e;
                selection-background-color: #f5d5e0;
                selection-color: #1c1c1e;
            }

            #titleSeparator {
                background: #f5d5e0;
                border: none;
            }
            #btnBold, #btnUnderline {
                background: #f5d5e0;
                color: #1c1c1e;
                border: none;
                border-radius: 4px;
                font-size: 13px;
                font-weight: 700;
            }
            #btnBold:hover, #btnUnderline:hover { background: #e8a0b5; }
            #btnBold:checked, #btnUnderline:checked {
                background: #e8a0b5;
                color: #ffffff;
            }

            #textEdit {
                border: none;
                background: #fff0f5;
                padding: 16px 20px;
                font-size: 14px;
                color: #1c1c1e;
                line-height: 1.6;
                selection-background-color: #f5d5e0;
                selection-color: #1c1c1e;
            }

            #actionBar {
                background: #fff0f5;
                border-top: 1px solid #f5d5e0;
            }
            #btnSave {
                background: #e8a0b5;
                color: #000000;
                border: none;
                border-radius: 6px;
                padding: 0 24px;
                font-size: 14pt;
                font-weight: 400;
            }
            #btnSave:hover { background: #df90a8; }
            #btnSave:pressed { background: #d6809b; }
            #btnSave:disabled { background: #f2ced8; }

            #btnDelete {
                background: #e8a0b5;
                color: #000000;
                border: none;
                border-radius: 6px;
                padding: 0 18px;
                font-size: 14pt;
                font-weight: 400;
            }
            #btnDelete:hover { background: #df90a8; }
            #btnDelete:pressed { background: #d6809b; }
            #btnDelete:disabled { background: #f2ced8; color: #000000; }

            QScrollBar:vertical {
                background: #fff0f5;
                width: 10px;
                margin: 0;
                border: none;
            }
            QScrollBar::handle:vertical {
                background: #f5d5e0;
                min-height: 30px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #e8a0b5;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
                background: none;
                border: none;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }

        """)

    def _set_editor_enabled(self, enabled: bool):
        self.title_edit.setEnabled(enabled)
        self.text_edit.setEnabled(enabled)
        self.btn_save.setEnabled(enabled)
        self.btn_delete.setEnabled(enabled)
        self.btn_bold.setEnabled(enabled)
        self.btn_underline.setEnabled(enabled)
        if not enabled:
            self.title_edit.clear()
            self.text_edit.clear()
            self.status_label.setText("")

    def _mark_dirty(self):
        if self.current_note_id is not None:
            self._dirty = True

    def _toggle_bold(self):
        fmt = self.text_edit.currentCharFormat()
        if fmt.fontWeight() == QFont.Weight.Bold:
            fmt.setFontWeight(QFont.Weight.Normal)
        else:
            fmt.setFontWeight(QFont.Weight.Bold)
        self.text_edit.mergeCurrentCharFormat(fmt)

    def _toggle_underline(self):
        fmt = self.text_edit.currentCharFormat()
        fmt.setFontUnderline(not fmt.fontUnderline())
        self.text_edit.mergeCurrentCharFormat(fmt)

    def _update_format_buttons(self):
        fmt = self.text_edit.currentCharFormat()
        self.btn_bold.setChecked(fmt.fontWeight() == QFont.Weight.Bold)
        self.btn_underline.setChecked(fmt.fontUnderline())

    def _load_notes(self):
        self.note_list.blockSignals(True)
        self.note_list.clear()
        for note_id, title in database.get_all_notes():
            display = title if title and title.strip() else "(Untitled)"
            item = QListWidgetItem(display)
            item.setData(Qt.ItemDataRole.UserRole, note_id)
            self.note_list.addItem(item)
        self.note_list.blockSignals(False)

    def _refresh_sidebar(self):
        self.note_list.blockSignals(True)
        for i in range(self.note_list.count()):
            item = self.note_list.item(i)
            note_id = item.data(Qt.ItemDataRole.UserRole)
            if note_id == self.current_note_id:
                title = self.title_edit.text().strip()
                item.setText(title if title else "(Untitled)")
                break
        self.note_list.blockSignals(False)

    def _select_note_by_id(self, note_id: int):
        for i in range(self.note_list.count()):
            item = self.note_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == note_id:
                self.note_list.setCurrentItem(item)
                return

# This function runs when the user clicks on a note in the sidebar
# First, it checks if the note currently open has unsaved changes
# If yes, a popup appears asking "do you want to save?" before anything else happens
# While that popup is open, the user might click another note by accident
# That would trigger this function a second time before the first one finished
# The _loading_note flag prevents that, if the function is already running, it stops immediately
# Once that's handled, the clicked note is fetched from the database and displayed in the editor with the correct font, scrolled to the top
    def _on_note_selected(self, current: QListWidgetItem, _previous):
        if current is None:
            self.current_note_id = None
            self._set_editor_enabled(False)
            return

        if self._loading_note:
            return
        self._loading_note = True

        try:
            if self._dirty:
                self._prompt_save()

            note_id = current.data(Qt.ItemDataRole.UserRole)
            note = database.get_note(note_id)
            if note is None:
                return

            self.current_note_id = note_id
            self._set_editor_enabled(True)

            self.title_edit.blockSignals(True)
            self.text_edit.blockSignals(True)
            self.title_edit.setText(note[1] or "")
            # toHtml() embeds inline "background-color:#ffffff" in the HTML body
            # Replace it with transparent so the editor's pink background shows through
            html = (note[2] or "").replace("background-color:#ffffff", "background-color:transparent")
            self.text_edit.setHtml(html)

            cursor = self.text_edit.textCursor()
            cursor.select(QTextCursor.SelectionType.Document)
            fmt = QTextCharFormat()
            fmt.setFontFamilies(["EB Garamond"])
            fmt.setFontPointSize(14)
            cursor.mergeCharFormat(fmt)
            cursor.clearSelection()
            # The font merge left the cursor at the end, which scrolled the editor to the bottom. Moving it to the start fixes that
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.text_edit.setTextCursor(cursor)
            self.title_edit.blockSignals(False)
            self.text_edit.blockSignals(False)

            self.status_label.setText("")
            self._dirty = False
        finally:
            self._loading_note = False

    def _new_note(self):
        if self._dirty:
            self._prompt_save()

        new_id = database.create_note("New note", "")
        self._load_notes()
        self._select_note_by_id(new_id)
        self.title_edit.setFocus()
        self.title_edit.selectAll()

    def _save_note(self):
        if self.current_note_id is None:
            return

        title = self.title_edit.text().strip()
        # Use toHtml instead of toPlainText to preserve line breaks and formatting
        text = self.text_edit.toHtml()

        if not title:
            QMessageBox.warning(self, "Missing title", "Please enter a title for the note.")
            self.title_edit.setFocus()
            return

        database.update_note(self.current_note_id, title, text)
        self._dirty = False

        self._refresh_sidebar()

    def _delete_note(self):
        if self.current_note_id is None:
            return

        reply = QMessageBox.question(
            self,
            "Delete note",
            "Are you sure you want to delete this note?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        database.delete_note(self.current_note_id)
        self.current_note_id = None
        self._dirty = False
        self._set_editor_enabled(False)
        self._load_notes()

    def _prompt_save(self):
        reply = QMessageBox.question(
            self,
            "Unsaved changes",
            "You have unsaved changes. Do you want to save them?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._save_note()
        self._dirty = False

    def closeEvent(self, event):
        if self._dirty:
            self._prompt_save()
        event.accept()


def main():
    # Tells Windows this process belongs to our app, not to pythonw.exe.
    # Without this, the taskbar shows a separate icon for the running process
    # instead of grouping it with the desktop shortcut.
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("notes.app")

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
    for filename in os.listdir(fonts_dir):
        if filename.endswith(".ttf"):
            QFontDatabase.addApplicationFont(os.path.join(fonts_dir, filename))

    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icons", "app_icon.ico")
    app.setWindowIcon(QIcon(icon_path))

    font = QFont("Cormorant Garamond", 12)
    app.setFont(font)
    window = NotesApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

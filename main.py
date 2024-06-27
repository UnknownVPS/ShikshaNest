import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTreeView, QFileSystemModel,
                             QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QPushButton,
                             QMessageBox, QInputDialog, QMenu, QAction, QTextEdit, QDialog,
                             QLabel, QListWidget, QFileDialog, QStyle, QToolBar, QSplitter,
                             QListView, QTabWidget, QPlainTextEdit)
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QDir, QSize
import shutil
import json
from datetime import datetime
import subprocess

STUDY_MATERIAL_ROOT = os.path.expanduser("~/StudyMaterial")

class CustomFileSystemModel(QFileSystemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.icons = {
            "Subject": QIcon("icons/folder.png"),
            "Teacher": QIcon("icons/user.png"),
            "Chapter": QIcon("icons/file-text.png"),
            "File": QIcon("icons/file.png"),
        }

    def icon(self, index):
        path = self.filePath(index)
        item_type = self.get_item_type(path)
        return self.icons.get(item_type, super().icon(index))

    def get_item_type(self, item_path):
        if os.path.isdir(item_path):
            parent_dir = os.path.abspath(os.path.dirname(item_path))
            grandparent_dir = os.path.abspath(os.path.dirname(parent_dir))

            if parent_dir == STUDY_MATERIAL_ROOT:
                return "Subject"
            elif grandparent_dir == STUDY_MATERIAL_ROOT:
                return "Teacher"
            else:
                return "Chapter"
        else:
            return "File"

class StudyMaterialManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Study Material Manager")
        self.setWindowIcon(QIcon('icons/logo.png'))
        self.setGeometry(100, 100, 1200, 800)
        self.notes = {}
        self.tags = {}
        self.flashcards = {}
        self.file_versions = {}
        self.load_metadata()
        self.setup_ui()

    def setup_ui(self):
        self.create_toolbar()
        
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setCentralWidget(main_widget)

        # Top bar with path, search, and home button
        top_bar_layout = QHBoxLayout()
        top_bar_layout.setContentsMargins(2, 2, 2, 2)
        top_bar_layout.setSpacing(2)
        main_layout.addLayout(top_bar_layout)
        
        self.home_button = QPushButton(QIcon("icons/home.png"), "")
        self.home_button.setFixedSize(24, 24)
        self.home_button.clicked.connect(self.go_home)
        top_bar_layout.addWidget(self.home_button)

        self.path_label = QLabel()
        self.path_label.setStyleSheet("font-weight: bold; padding: 0 2px;")
        top_bar_layout.addWidget(self.path_label, 1)
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search...")
        self.search_bar.setMaximumWidth(200)
        self.search_bar.setFixedHeight(24)
        search_button = QPushButton(QIcon("icons/search.png"), "")
        search_button.setFixedSize(24, 24)
        search_button.clicked.connect(self.search)
        top_bar_layout.addWidget(self.search_bar)
        top_bar_layout.addWidget(search_button)

        # Main splitter
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setHandleWidth(1)
        main_layout.addWidget(main_splitter)

        # Left panel (Tree view)
        self.tree_model = CustomFileSystemModel()
        self.tree_model.setRootPath(STUDY_MATERIAL_ROOT)
        self.tree = QTreeView()
        self.tree.setModel(self.tree_model)
        self.tree.setRootIndex(self.tree_model.index(STUDY_MATERIAL_ROOT))
        self.tree.setAnimated(False)
        self.tree.setIndentation(15)
        self.tree.setSortingEnabled(True)
        self.tree.setColumnWidth(0, 250)
        self.tree.setEditTriggers(QTreeView.NoEditTriggers)
        self.tree.setDragEnabled(True)
        self.tree.setAcceptDrops(True)
        self.tree.setDropIndicatorShown(True)
        self.tree.setDragDropMode(QTreeView.InternalMove)
        self.tree.setHeaderHidden(True)
        self.tree.setColumnHidden(1, True)
        self.tree.setColumnHidden(2, True)
        self.tree.setColumnHidden(3, True)
        self.tree.clicked.connect(self.tree_item_clicked)
        main_splitter.addWidget(self.tree)

        # Right panel (List view)
        self.list_model = QStandardItemModel()
        self.list_view = QListView()
        self.list_view.setModel(self.list_model)
        self.list_view.setEditTriggers(QListView.NoEditTriggers)
        self.list_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_view.customContextMenuRequested.connect(self.show_context_menu)
        self.list_view.clicked.connect(self.list_item_clicked)
        self.list_view.doubleClicked.connect(self.list_item_double_clicked)
        main_splitter.addWidget(self.list_view)

        main_splitter.setSizes([int(self.width() * 0.3), int(self.width() * 0.7)])

        self.set_modern_theme()
        self.go_home()  # Set initial view to subjects

    def create_toolbar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setStyleSheet("QToolBar { spacing: 1px; padding: 1px; }")
        self.addToolBar(toolbar)
        
        add_subject_action = QAction(QIcon("icons/folder-plus.png"), "Add Subject", self)
        add_subject_action.triggered.connect(lambda: self.add_item("Subject"))
        toolbar.addAction(add_subject_action)

        add_teacher_action = QAction(QIcon("icons/user-plus.png"), "Add Teacher", self)
        add_teacher_action.triggered.connect(lambda: self.add_item("Teacher"))
        toolbar.addAction(add_teacher_action)

        add_chapter_action = QAction(QIcon("icons/file-plus.png"), "Add Chapter", self)
        add_chapter_action.triggered.connect(lambda: self.add_item("Chapter"))
        toolbar.addAction(add_chapter_action)

        add_file_action = QAction(QIcon("icons/upload.png"), "Add File", self)
        add_file_action.triggered.connect(self.add_file)
        toolbar.addAction(add_file_action)

    def set_modern_theme(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QTreeView, QListView {
                background-color: #363636;
                border: none;
                color: #ffffff;
            }
            QTreeView::item, QListView::item {
                padding: 2px;
            }
            QTreeView::item:selected, QListView::item:selected {
                background-color: #4a4a4a;
            }
            QLineEdit {
                background-color: #363636;
                color: #ffffff;
                padding: 2px;
                border: 1px solid #1e1e1e;
                border-radius: 2px;
            }
            QPushButton {
                background-color: #0d47a1;
                color: white;
                padding: 2px 5px;
                border: none;
                border-radius: 2px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QToolBar {
                background-color: #1e1e1e;
                spacing: 1px;
                padding: 1px;
            }
            QToolButton {
                background-color: transparent;
                border: none;
                border-radius: 2px;
                padding: 1px;
            }
            QToolButton:hover {
                background-color: #363636;
            }
            QLabel {
                color: #ffffff;
            }
            QMenu {
                background-color: #363636;
                color: #ffffff;
                border: 1px solid #1e1e1e;
            }
            QMenu::item:selected {
                background-color: #4a4a4a;
            }
            QScrollBar:vertical {
                border: none;
                background: #363636;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #666666;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QSplitter::handle {
                background-color: #1e1e1e;
            }
        """)

    def go_home(self):
        self.update_ui(STUDY_MATERIAL_ROOT)
        self.tree.setCurrentIndex(self.tree_model.index(STUDY_MATERIAL_ROOT))
        self.tree.collapseAll()

    def tree_item_clicked(self, index):
        path = self.tree_model.filePath(index)
        if os.path.isdir(path):
            self.update_ui(path)

    def list_item_clicked(self, index):
        item_path = self.get_item_path_from_index(index)
        if os.path.isdir(item_path):
            self.update_ui(item_path)

    def list_item_double_clicked(self, index):
        item_path = self.get_item_path_from_index(index)
        if os.path.isdir(item_path):
            self.update_ui(item_path)
            tree_index = self.tree_model.index(item_path)
            self.tree.setCurrentIndex(tree_index)
            self.tree.expand(tree_index)
        else:
            self.open_file(item_path)

    def get_item_path_from_index(self, index):
        item = self.list_model.itemFromIndex(index)
        current_path = os.path.join(STUDY_MATERIAL_ROOT, self.path_label.text())
        return os.path.join(current_path, item.text())

    def open_file(self, path):
        if sys.platform.startswith('darwin'):  # macOS
            subprocess.call(('open', path))
        elif os.name == 'nt':  # Windows
            os.startfile(path)
        elif os.name == 'posix':  # Linux
            subprocess.call(('xdg-open', path))

    def search(self):
        search_term = self.search_bar.text().lower()
        if not search_term:
            return

        self.list_model.clear()
        self.search_recursive(STUDY_MATERIAL_ROOT, search_term)
        self.update_path_label(STUDY_MATERIAL_ROOT)  # Reset path label to root when searching

    def search_recursive(self, path, search_term):
        for item in os.listdir(path):
            if item.startswith('.'):
                continue
            item_path = os.path.join(path, item)
            if search_term in item.lower() or (item_path in self.tags and search_term in ' '.join(self.tags[item_path]).lower()):
                relative_path = os.path.relpath(item_path, STUDY_MATERIAL_ROOT)
                icon = self.tree_model.icons.get(self.tree_model.get_item_type(item_path), self.style().standardIcon(QStyle.SP_FileIcon))
                list_item = QStandardItem(icon, relative_path)
                self.list_model.appendRow(list_item)
            
            if os.path.isdir(item_path):
                self.search_recursive(item_path, search_term)

    def show_context_menu(self, position):
        global_pos = self.list_view.mapToGlobal(position)
        index = self.list_view.indexAt(position)
        if not index.isValid():
            return

        item_path = self.get_item_path_from_index(index)

        menu = QMenu()
        delete_action = menu.addAction(self.style().standardIcon(QStyle.SP_TrashIcon), "Delete")
        note_action = menu.addAction(self.style().standardIcon(QStyle.SP_FileDialogDetailedView), "Add/Edit Note")
        tag_action = menu.addAction(self.style().standardIcon(QStyle.SP_FileDialogInfoView), "Manage Tags")
        flashcard_action = menu.addAction(self.style().standardIcon(QStyle.SP_FileDialogContentsView), "Manage Flashcards")
        version_action = menu.addAction(self.style().standardIcon(QStyle.SP_FileDialogDetailedView), "Version")
        if os.path.isfile(item_path):
            version_action = menu.addAction(self.style().standardIcon(QStyle.SP_FileIcon), "Show Versions")

        action = menu.exec_(global_pos)

        if action == delete_action:
            self.delete_item(item_path)
        elif action == note_action:
            self.manage_note(item_path)
        elif action == tag_action:
            self.manage_tags(item_path)
        elif action == flashcard_action:
            self.manage_flashcards(item_path)
        elif action == version_action:
            self.show_versions(item_path)

    def show_versions(self, path):
        if path in self.file_versions:
            versions = self.file_versions[path]
            dialog = QDialog(self)
            dialog.setWindowTitle("File Versions")
            layout = QVBoxLayout()
            
            version_list = QListWidget()
            for version in versions:
                version_list.addItem(f"Timestamp: {version['timestamp']}")
            layout.addWidget(version_list)

            button_layout = QHBoxLayout()
            view_button = QPushButton("View")
            close_button = QPushButton("Close")
            button_layout.addWidget(view_button)
            button_layout.addWidget(close_button)
            layout.addLayout(button_layout)
            
            dialog.setLayout(layout)
            
            def view_version():
                current = version_list.currentRow()
                if current >= 0:
                    content = versions[current]['content']
                    view_dialog = QDialog(dialog)
                    view_dialog.setWindowTitle(f"Version {current + 1}")
                    view_layout = QVBoxLayout()
                    text_edit = QTextEdit()
                    text_edit.setPlainText(content)
                    view_layout.addWidget(text_edit)
                    close_view_button = QPushButton("Close")
                    close_view_button.clicked.connect(view_dialog.accept)
                    view_layout.addWidget(close_view_button)
                    view_dialog.setLayout(view_layout)
                    view_dialog.exec_()
            
            view_button.clicked.connect(view_version)
            close_button.clicked.connect(dialog.accept)
            
            dialog.exec_()

    def delete_item(self, path):
        reply = QMessageBox.question(self, 'Delete Confirmation',
                                     f"Are you sure you want to delete '{path}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                if os.path.isfile(path):
                    os.remove(path)
                else:
                    shutil.rmtree(path)
                self.update_ui(os.path.dirname(path))
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not delete item: {str(e)}")

    def manage_note(self, path):
        current_note = self.notes.get(path, "")
        note, ok = QInputDialog.getMultiLineText(self, "Manage Note", "Enter note:", current_note)
        if ok:
            self.notes[path] = note
            self.save_metadata()

    def manage_tags(self, path):
        current_tags = self.tags.get(path, [])
        tags, ok = QInputDialog.getText(self, "Manage Tags", "Enter tags (comma-separated):", text=",".join(current_tags))
        if ok:
            self.tags[path] = [tag.strip() for tag in tags.split(",") if tag.strip()]
            self.save_metadata()

    def manage_flashcards(self, path):
        if path not in self.flashcards:
            self.flashcards[path] = []
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Manage Flashcards")
        layout = QVBoxLayout()

        flashcard_list = QListWidget()
        for card in self.flashcards[path]:
            flashcard_list.addItem(f"Q: {card['question']}")
        layout.addWidget(flashcard_list)

        button_layout = QHBoxLayout()
        add_button = QPushButton("Add")
        edit_button = QPushButton("Edit")
        delete_button = QPushButton("Delete")
        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)

        def add_flashcard():
            question, ok1 = QInputDialog.getText(dialog, "Add Flashcard", "Enter question:")
            if ok1:
                answer, ok2 = QInputDialog.getText(dialog, "Add Flashcard", "Enter answer:")
                if ok2:
                    self.flashcards[path].append({"question": question, "answer": answer})
                    flashcard_list.addItem(f"Q: {question}")
                    self.save_metadata()

        def edit_flashcard():
            current = flashcard_list.currentRow()
            if current >= 0:
                card = self.flashcards[path][current]
                question, ok1 = QInputDialog.getText(dialog, "Edit Flashcard", "Edit question:", text=card['question'])
                if ok1:
                    answer, ok2 = QInputDialog.getText(dialog, "Edit Flashcard", "Edit answer:", text=card['answer'])
                    if ok2:
                        self.flashcards[path][current] = {"question": question, "answer": answer}
                        flashcard_list.item(current).setText(f"Q: {question}")
                        self.save_metadata()

        def delete_flashcard():
            current = flashcard_list.currentRow()
            if current >= 0:
                del self.flashcards[path][current]
                flashcard_list.takeItem(current)
                self.save_metadata()

        add_button.clicked.connect(add_flashcard)
        edit_button.clicked.connect(edit_flashcard)
        delete_button.clicked.connect(delete_flashcard)

        dialog.exec_()

    def add_file(self):
        current_path = os.path.join(STUDY_MATERIAL_ROOT, self.path_label.text())
        
        if os.path.dirname(os.path.dirname(os.path.dirname(current_path))) == STUDY_MATERIAL_ROOT:
            file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*)")
            if file_path:
                dest_path = os.path.join(current_path, os.path.basename(file_path))
                shutil.copy(file_path, dest_path)
                self.update_ui(current_path)
                self.add_file_version(dest_path)
        else:
            QMessageBox.warning(self, "Invalid Selection", "Please select a Chapter to add a file.")

    def add_file_version(self, path):
        if path not in self.file_versions:
            self.file_versions[path] = []
        
        file_stat = os.stat(path)
        version = {
            'content': f"File size: {file_stat.st_size} bytes, Last modified: {datetime.fromtimestamp(file_stat.st_mtime)}",
            'timestamp': datetime.now().isoformat()
        }
        self.file_versions[path].append(version)
        self.save_metadata()

    def add_item(self, item_type):
        current_path = os.path.join(STUDY_MATERIAL_ROOT, self.path_label.text())
        
        if item_type == "Subject":
            parent_path = STUDY_MATERIAL_ROOT
        elif item_type == "Teacher":
            if os.path.dirname(current_path) == STUDY_MATERIAL_ROOT:
                parent_path = current_path
            else:
                QMessageBox.warning(self, "Invalid Selection", "Please select a Subject to add a Teacher.")
                return
        elif item_type == "Chapter":
            if os.path.dirname(os.path.dirname(current_path)) == STUDY_MATERIAL_ROOT:
                parent_path = current_path
            else:
                QMessageBox.warning(self, "Invalid Selection", "Please select a Teacher to add a Chapter.")
                return
        else:
            QMessageBox.warning(self, "Invalid Item Type", f"Cannot add item of type {item_type}")
            return

        name, ok = QInputDialog.getText(self, f"Add {item_type}", f"Enter {item_type} name:")
        if ok and name:
            new_path = os.path.join(parent_path, name)
            os.makedirs(new_path, exist_ok=True)
            self.update_ui(parent_path)
            tree_index = self.tree_model.index(new_path)
            self.tree.setCurrentIndex(tree_index)
            self.tree.expand(tree_index)

    def update_ui(self, path):
        self.update_list_view(path)
        self.update_path_label(path)

    def update_list_view(self, path):
        self.list_model.clear()
        for item in os.listdir(path):
            if not item.startswith('.'):  # Skip hidden files
                item_path = os.path.join(path, item)
                item_type = self.tree_model.get_item_type(item_path)
                icon = self.tree_model.icons.get(item_type, self.style().standardIcon(QStyle.SP_FileIcon))
                list_item = QStandardItem(icon, item)
                self.list_model.appendRow(list_item)

    def update_path_label(self, path):
        relative_path = os.path.relpath(path, STUDY_MATERIAL_ROOT)
        self.path_label.setText(relative_path)

    def load_metadata(self):
        metadata_file = os.path.join(STUDY_MATERIAL_ROOT, ".study_metadata.json")
        if os.path.exists(metadata_file):
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
                self.notes = metadata.get("notes", {})
                self.tags = metadata.get("tags", {})
                self.flashcards = metadata.get("flashcards", {})
                self.file_versions = metadata.get("file_versions", {})

    def save_metadata(self):
        metadata_file = os.path.join(STUDY_MATERIAL_ROOT, ".study_metadata.json")
        metadata = {
            "notes": self.notes,
            "tags": self.tags,
            "flashcards": self.flashcards,
            "file_versions": self.file_versions
        }
        with open(metadata_file, "w") as f:
            json.dump(metadata, f)

if __name__ == "__main__":
    if not os.path.exists(STUDY_MATERIAL_ROOT):
        os.makedirs(STUDY_MATERIAL_ROOT)
    app = QApplication(sys.argv)
    
    window = StudyMaterialManager()
    window.show()
    sys.exit(app.exec_())
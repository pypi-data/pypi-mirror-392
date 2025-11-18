import sys
import os
import difflib
import subprocess
import tempfile

try:
    from PySide6.QtWidgets import (
        QAbstractItemView, QApplication, QCheckBox, QComboBox,
        QDialog, QDialogButtonBox, QFileDialog, QFormLayout, QGroupBox,
        QHeaderView, QHBoxLayout, QInputDialog, QLabel, QLineEdit,
        QMainWindow, QMenu, QMessageBox, QPushButton, QRadioButton, QSplitter,
        QStackedWidget, QStyle, QTableWidget, QTableWidgetItem, QTextBrowser,
        QTextEdit, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
    )
    from PySide6.QtGui import QColor, QBrush, QFont, QPainter, QPixmap, QIcon
    from PySide6.QtCore import QFile, QTextStream, Qt
except ImportError:
    print("ERRO: A dependência 'PySide6' não está instalada. Por favor, execute: pip install PySide6")
    sys.exit(1)

try:
    import markdown2
except ImportError:
    print("ERRO: A dependência 'markdown2' não está instalada. Por favor, execute: pip install markdown2")
    sys.exit(1)

from gitsnap.core import git_repo, snapshots, config, git_push
from gitsnap.core.errors import GitSnapError, NoChangesError, RepositoryNotInitializedError

def set_tooltip_if_enabled(widget: QWidget, text: str):
    """Define o tooltip para um widget apenas se a configuração estiver ativa."""
    settings = config.load_config()
    if settings.get("show_tooltips", True):
        widget.setToolTip(text)

class FilterSortDialog(QDialog):
    def __init__(self, sort_options, type_options, current_sort, current_filter, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ordenar e Filtrar")
        
        self.main_layout = QVBoxLayout(self)
        
        # Sorting Group
        self.sort_group = QGroupBox("Ordenar por")
        self.sort_layout = QVBoxLayout()
        self.sort_buttons = {}
        for option in sort_options:
            radio = QRadioButton(option)
            if option == current_sort:
                radio.setChecked(True)
            self.sort_layout.addWidget(radio)
            self.sort_buttons[option] = radio
        self.sort_group.setLayout(self.sort_layout)
        
        # Filtering Group
        self.filter_group = QGroupBox("Filtrar por tipo")
        self.filter_layout = QVBoxLayout()
        self.filter_buttons = {}
        
        all_types_radio = QRadioButton("Todos os Tipos")
        if current_filter == "Todos os Tipos":
            all_types_radio.setChecked(True)
        self.filter_layout.addWidget(all_types_radio)
        self.filter_buttons["Todos os Tipos"] = all_types_radio
        
        for option in type_options:
            radio = QRadioButton(option)
            if option == current_filter:
                radio.setChecked(True)
            self.filter_layout.addWidget(radio)
            self.filter_buttons[option] = radio
        self.filter_group.setLayout(self.filter_layout)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.button(QDialogButtonBox.Ok).setText("Aplicar")
        button_box.button(QDialogButtonBox.Cancel).setText("Cancelar")
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        self.main_layout.addWidget(self.sort_group)
        self.main_layout.addWidget(self.filter_group)
        self.main_layout.addWidget(button_box)

    def get_values(self):
        selected_sort = ""
        for option, radio in self.sort_buttons.items():
            if radio.isChecked():
                selected_sort = option
                break
        
        selected_filter = ""
        for option, radio in self.filter_buttons.items():
            if radio.isChecked():
                selected_filter = option
                break
                
        return selected_sort, selected_filter

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajuda do GitSnap")
        self.setMinimumSize(600, 500)
        layout = QVBoxLayout(self)
        help_browser = QTextBrowser()
        help_browser.setOpenExternalLinks(True)
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            help_file_path = os.path.join(script_dir, "assets", "help.md")
            with open(help_file_path, "r", encoding="utf-8") as f:
                md_content = f.read()
            html = markdown2.markdown(md_content, extras=["fenced-code-blocks"])
            help_browser.setHtml(html)
        except FileNotFoundError:
            help_browser.setHtml("<h1>Erro</h1><p>Ficheiro de ajuda não encontrado.</p>")
        layout.addWidget(help_browser)

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurações")
        layout = QFormLayout(self)
        self.username_input = QLineEdit()
        self.email_input = QLineEdit()
        self.show_tooltips_checkbox = QCheckBox("Mostrar dicas de ajuda nos botões")
        layout.addRow("Nome de utilizador:", self.username_input)
        layout.addRow("Email:", self.email_input)
        layout.addRow("", self.show_tooltips_checkbox)
        
        button_box = QDialogButtonBox()
        save_button = button_box.addButton("Guardar", QDialogButtonBox.AcceptRole)
        cancel_button = button_box.addButton("Cancelar", QDialogButtonBox.RejectRole)
        
        save_button.clicked.connect(self.save_settings)
        cancel_button.clicked.connect(self.reject)
        
        layout.addWidget(button_box)
        self.load_settings()

    def load_settings(self):
        settings = config.load_config()
        self.username_input.setText(settings.get("username", ""))
        self.email_input.setText(settings.get("email", ""))
        self.show_tooltips_checkbox.setChecked(settings.get("show_tooltips", True))

    def save_settings(self):
        current_config = config.load_config()
        repo_url = current_config.get("repo_url", "")
        settings = {
            "username": self.username_input.text(),
            "email": self.email_input.text(),
            "show_tooltips": self.show_tooltips_checkbox.isChecked(),
            "repo_url": repo_url
        }
        config.save_config(settings)
        QMessageBox.information(self, "Sucesso", "Configurações guardadas.")
        self.accept()

class CreateSnapshotDialog(QDialog):
    def __init__(self, parent=None, existing_types=None):
        super().__init__(parent)
        self.setWindowTitle("Criar Snapshot")
        layout = QFormLayout(self)
        self.internal_name_input = QLineEdit()
        self.tag_input = QLineEdit()
        self.message_input = QLineEdit()
        self.type_combo = QComboBox()
        self.type_combo.setEditable(True)
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Descrição detalhada em formato Markdown...")

        if existing_types:
            self.type_combo.addItems(sorted(list(existing_types)))
        self.type_combo.insertItem(0, "none")
        self.type_combo.setCurrentText("none")

        layout.addRow("Nome interno:", self.internal_name_input)
        layout.addRow("Tag:", self.tag_input)
        layout.addRow("Mensagem:", self.message_input)
        layout.addRow("Tipo:", self.type_combo)
        layout.addRow("Descrição:", self.description_input)
        
        button_box = QDialogButtonBox()
        ok_button = button_box.addButton("Criar", QDialogButtonBox.AcceptRole)
        cancel_button = button_box.addButton("Cancelar", QDialogButtonBox.RejectRole)
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        layout.addWidget(button_box)

    def get_values(self):
        return (
            self.internal_name_input.text(),
            self.tag_input.text(),
            self.message_input.text(),
            self.type_combo.currentText(),
            self.description_input.toPlainText()
        )

class EditSnapshotDialog(QDialog):
    def __init__(self, old_internal_name, old_tag, old_message, old_type, old_description, existing_types, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editar Snapshot")
        layout = QFormLayout(self)
        self.internal_name_input = QLineEdit(old_internal_name)
        self.tag_input = QLineEdit(old_tag)
        self.message_input = QLineEdit(old_message)
        self.type_combo = QComboBox()
        self.type_combo.setEditable(True)
        self.description_input = QTextEdit(old_description)
        self.description_input.setPlaceholderText("Descrição detalhada em formato Markdown...")
        
        if existing_types:
            self.type_combo.addItems(sorted(list(existing_types)))
        
        if old_type not in existing_types:
            self.type_combo.addItem(old_type)
            
        self.type_combo.setCurrentText(old_type)

        layout.addRow("Nome Interno:", self.internal_name_input)
        layout.addRow("Tag:", self.tag_input)
        layout.addRow("Mensagem:", self.message_input)
        layout.addRow("Tipo:", self.type_combo)
        layout.addRow("Descrição:", self.description_input)
        
        button_box = QDialogButtonBox()
        ok_button = button_box.addButton("Guardar", QDialogButtonBox.AcceptRole)
        cancel_button = button_box.addButton("Cancelar", QDialogButtonBox.RejectRole)
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        layout.addWidget(button_box)

    def get_values(self):
        return (
            self.internal_name_input.text(),
            self.tag_input.text(),
            self.message_input.text(),
            self.type_combo.currentText(),
            self.description_input.toPlainText()
        )

class PullDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pull do GitHub")
        self.layout = QFormLayout(self)
        self.repo_url_input = QLineEdit()
        self.token_input = QLineEdit()
        self.token_input.setEchoMode(QLineEdit.Password)
        self.layout.addRow("URL do Repositório:", self.repo_url_input)
        self.layout.addRow("Token do GitHub:", self.token_input)
        
        self.button_box = QDialogButtonBox()
        pull_button = self.button_box.addButton("Pull", QDialogButtonBox.AcceptRole)
        cancel_button = self.button_box.addButton("Cancelar", QDialogButtonBox.RejectRole)
        pull_button.clicked.connect(self.pull_changes)
        cancel_button.clicked.connect(self.reject)
        
        self.layout.addWidget(self.button_box)
        saved_config = config.load_config()
        self.repo_url_input.setText(saved_config.get("repo_url", ""))

    def pull_changes(self):
        repo_url = self.repo_url_input.text()
        token = self.token_input.text()
        if not all([repo_url, token]):
            QMessageBox.warning(self, "Erro de Entrada", "URL do Repositório e Token são obrigatórios.")
            return
        status, message = git_push.pull_from_remote(repo_url, token)
        if status == "success":
            QMessageBox.information(self, "Sucesso", message)
            self.accept()
        elif status == "conflict":
            QMessageBox.warning(self, "Conflito", message)
        else:
            QMessageBox.critical(self, "Erro", message)

class PushSnapshotDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Push de Snapshot para o GitHub")
        self.layout = QFormLayout(self)
        self.snaps = []
        self.snapshot_combo = QComboBox()
        self.repo_url_input = QLineEdit()
        self.message_input = QLineEdit()
        self.token_input = QLineEdit()
        self.token_input.setEchoMode(QLineEdit.Password)
        self.layout.addRow("Snapshot:", self.snapshot_combo)
        self.layout.addRow("URL do Repositório:", self.repo_url_input)
        self.layout.addRow("Mensagem do Push:", self.message_input)
        self.layout.addRow("Token do GitHub:", self.token_input)
        self.button_box = QDialogButtonBox()
        self.sync_button = self.button_box.addButton("Sincronizar", QDialogButtonBox.ActionRole)
        set_tooltip_if_enabled(self.sync_button, "Puxa as alterações do GitHub e depois envia o seu snapshot.")
        self.push_button = self.button_box.addButton("Push", QDialogButtonBox.AcceptRole)
        set_tooltip_if_enabled(self.push_button, "Envia o snapshot selecionado para o GitHub.")
        self.cancel_button = self.button_box.addButton("Cancelar", QDialogButtonBox.RejectRole)
        self.push_button.clicked.connect(self.push_snapshot)
        self.sync_button.clicked.connect(self.sync_and_push)
        self.cancel_button.clicked.connect(self.reject)
        self.layout.addWidget(self.button_box)
        self.snapshot_combo.currentIndexChanged.connect(self.update_message)
        self.load_snapshots()
        saved_config = config.load_config()
        self.repo_url_input.setText(saved_config.get("repo_url", ""))

    def load_snapshots(self):
        try:
            self.snaps = snapshots.list_snapshots()
            self.snapshot_combo.clear()
            for snap in self.snaps:
                self.snapshot_combo.addItem(snap.tag)
            if not self.snaps:
                self.message_input.setPlaceholderText("Nenhum snapshot local para selecionar")
                self.snapshot_combo.setEnabled(False)
                self.push_button.setEnabled(False)
                self.sync_button.setEnabled(False)
        except GitSnapError as e:
            QMessageBox.critical(self, "Erro", f"Não foi possível carregar os snapshots: {e}")

    def update_message(self, index):
        if 0 <= index < len(self.snaps):
            self.message_input.setText(self.snaps[index].message)

    def _get_form_data(self):
        snapshot_tag = self.snapshot_combo.currentText()
        repo_url = self.repo_url_input.text()
        token = self.token_input.text()
        push_message = self.message_input.text()
        if not all([snapshot_tag, repo_url, token]):
            QMessageBox.warning(self, "Erro de Entrada", "Snapshot, URL do Repositório e Token são obrigatórios.")
            return None
        if not push_message:
            current_index = self.snapshot_combo.currentIndex()
            if 0 <= current_index < len(self.snaps):
                push_message = self.snaps[current_index].message
            else:
                QMessageBox.warning(self, "Erro de Entrada", "Não foi possível determinar a mensagem para o snapshot.")
                return None
        return snapshot_tag, repo_url, token, push_message

    def push_snapshot(self):
        data = self._get_form_data()
        if data is None: return
        snapshot_tag, repo_url, token, push_message = data
        status, message = git_push.push_snapshot(snapshot_tag=snapshot_tag, repo_url=repo_url, token=token, push_message=push_message)
        self._handle_operation_result(status, message, repo_url)

    def sync_and_push(self):
        data = self._get_form_data()
        if data is None: return
        snapshot_tag, repo_url, token, push_message = data
        status, message = git_push.sync_with_remote(snapshot_tag=snapshot_tag, repo_url=repo_url, token=token, push_message=push_message)
        self._handle_operation_result(status, message, repo_url)

    def _handle_operation_result(self, status: str, message: str, repo_url: str):
        if status == "success" or status == "already_up_to_date":
            try:
                current_config = config.load_config()
                current_config['repo_url'] = repo_url
                config.save_config(current_config)
            except Exception as e:
                QMessageBox.warning(self, "Aviso", f"Não foi possível guardar o URL do repositório: {e}")
            QMessageBox.information(self, "Sucesso", message)
            self.accept()
        elif status == "conflict":
            QMessageBox.warning(self, "Conflito", message)
        else:
            QMessageBox.critical(self, "Erro", message)

STATUS_COLORS = {'igual': Qt.green, 'modificado': Qt.yellow, 'missing': Qt.red}

def open_file(path: str):
    """Abre um ficheiro com a aplicação padrão do sistema operativo."""
    if sys.platform.startswith("darwin"):
        subprocess.run(["open", path], check=False)
    elif os.name == "nt":
        os.startfile(path)
    elif os.name == "posix":
        subprocess.run(["xdg-open", path], check=False)
    else:
        print(f"Plataforma não suportada para abrir ficheiros: {sys.platform}")

def create_status_icon(color: QColor) -> QIcon:
    pixmap = QPixmap(16, 16); pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap); painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QBrush(color)); painter.setPen(Qt.NoPen)
    painter.drawEllipse(0, 0, 16, 16); painter.end()
    return QIcon(pixmap)

class FileDiffDialog(QDialog):
    def __init__(self, title, file_path, content1, content2, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title); self.setGeometry(200, 200, 900, 700)
        diff_text = "".join(difflib.unified_diff(
            content1.splitlines(keepends=True), content2.splitlines(keepends=True),
            fromfile=f"a/{file_path}", tofile=f"b/{file_path}"
        ))
        text_edit = QTextEdit(diff_text); text_edit.setReadOnly(True)
        font = QFont("monospace"); font.setStyleHint(QFont.TypeWriter); text_edit.setFont(font)
        layout = QVBoxLayout(self); layout.addWidget(text_edit)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok); button_box.accepted.connect(self.accept)
        button_box.button(QDialogButtonBox.Ok).setText("Fechar")
        layout.addWidget(button_box)

class BaseComparisonWindow(QDialog):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title); self.setGeometry(150, 150, 1200, 800)
        self.status_icons = {s: create_status_icon(c) for s, c in STATUS_COLORS.items()}

    def _create_tree(self) -> QTreeWidget:
        tree = QTreeWidget(); tree.setHeaderLabels(["Nome", "Tipo", "Status"])
        tree.setColumnCount(3); tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        return tree

    def _populate_tree(self, tree_widget: QTreeWidget, data: list):
        tree_widget.clear()
        nodes = {"": tree_widget.invisibleRootItem()}
        for item in data:
            path = item['name']; parts = path.split('/')
            parent_node = nodes[""]; parent_path_key = ""
            for part in parts[:-1]:
                parent_path_key = os.path.join(parent_path_key, part)
                if parent_path_key not in nodes:
                    parent_node = QTreeWidgetItem(parent_node, [part])
                    nodes[parent_path_key] = parent_node
                else:
                    parent_node = nodes[parent_path_key]
            node_item = QTreeWidgetItem(parent_node, [parts[-1], item['type'], item['status']])
            node_item.setIcon(0, self.status_icons.get(item['status']))
            node_item.setData(0, Qt.UserRole, item['name']); node_item.setData(2, Qt.UserRole, item['status'])
        self._update_folder_statuses(tree_widget.invisibleRootItem())
        tree_widget.collapseAll()

    def _update_folder_statuses(self, root_item: QTreeWidgetItem):
        for i in range(root_item.childCount()): self._set_folder_status_recursively(root_item.child(i))

    def _set_folder_status_recursively(self, item: QTreeWidgetItem) -> int:
        severity_map = {'missing': 2, 'modificado': 1, 'igual': 0}
        status_map = {v: k for k, v in severity_map.items()}
        if item.childCount() == 0: return severity_map.get(item.data(2, Qt.UserRole), 0)
        max_child_severity = 0
        for i in range(item.childCount()):
            max_child_severity = max(max_child_severity, self._set_folder_status_recursively(item.child(i)))
        final_status = status_map[max_child_severity]
        item.setText(2, final_status); item.setIcon(0, self.status_icons.get(final_status))
        item.setData(2, Qt.UserRole, final_status)
        return max_child_severity

    def _open_temp_snapshot_file(self, tag: str, file_path: str):
        """Helper para extrair e abrir um ficheiro de um snapshot."""
        try:
            content = snapshots.get_file_content_from_snapshot(tag, file_path)
            if content is None:
                self.parent().show_error_message(f"Ficheiro '{file_path}' não encontrado no snapshot '{tag}'.")
                return
            
            _, extension = os.path.splitext(file_path)
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=extension, encoding='utf-8') as tmp_file:
                tmp_file.write(content)
                tmp_file_path = tmp_file.name
            
            self.parent().status_label.setText(f"A abrir cópia temporária de '{file_path}' do snapshot '{tag}'...")
            open_file(tmp_file_path)
        except (GitSnapError, IOError) as e:
            QMessageBox.critical(self, "Erro", f"Não foi possível abrir o ficheiro temporário: {e}")

class LocalComparisonWindow(BaseComparisonWindow):
    def __init__(self, tag: str, parent=None):
        super().__init__(f"Comparação: Snapshot '{tag}' vs. Local", parent)
        self.tag = tag
        self.tree1 = self._create_tree(); self.tree2 = self._create_tree()
        splitter = QSplitter(Qt.Horizontal); splitter.addWidget(self.tree1); splitter.addWidget(self.tree2)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok); button_box.accepted.connect(self.accept)
        button_box.button(QDialogButtonBox.Ok).setText("Fechar")
        layout = QVBoxLayout(self); layout.addWidget(splitter); layout.addWidget(button_box)
        self.tree1.itemDoubleClicked.connect(self.handle_double_click)
        self.tree2.itemDoubleClicked.connect(self.handle_double_click)
        self.load_comparison()

    def load_comparison(self):
        try:
            files1, files2 = snapshots.compare_snapshot_with_local_side_by_side(self.tag)
            self._populate_tree(self.tree1, files1); self._populate_tree(self.tree2, files2)
        except GitSnapError as e: QMessageBox.critical(self, "Erro", f"Não foi possível gerar a comparação: {e}")

    def handle_double_click(self, item: QTreeWidgetItem):
        if item.text(1) != 'file': return
        file_path = item.data(0, Qt.UserRole)
        if os.path.exists(file_path):
            open_file(file_path)
        else:
            self._open_temp_snapshot_file(self.tag, file_path)

class TwoSnapshotComparisonWindow(BaseComparisonWindow):
    def __init__(self, tag1: str, tag2: str, parent=None):
        super().__init__(f"Comparação: '{tag1}' vs. '{tag2}'", parent)
        self.tag1, self.tag2 = tag1, tag2
        self.tree1 = self._create_tree(); self.tree2 = self._create_tree()
        splitter = QSplitter(Qt.Horizontal); splitter.addWidget(self.tree1); splitter.addWidget(self.tree2)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok); button_box.accepted.connect(self.accept)
        button_box.button(QDialogButtonBox.Ok).setText("Fechar")
        layout = QVBoxLayout(self); layout.addWidget(splitter); layout.addWidget(button_box)
        self.tree1.itemDoubleClicked.connect(lambda item: self._open_temp_snapshot_file(self.tag1, item.data(0, Qt.UserRole)) if item.text(1) == 'file' else None)
        self.tree2.itemDoubleClicked.connect(lambda item: self._open_temp_snapshot_file(self.tag2, item.data(0, Qt.UserRole)) if item.text(1) == 'file' else None)
        self.load_comparison()

    def load_comparison(self):
        try:
            files1, files2 = snapshots.compare_snapshots_side_by_side(self.tag1, self.tag2)
            self._populate_tree(self.tree1, files1); self._populate_tree(self.tree2, files2)
        except GitSnapError as e: QMessageBox.critical(self, "Erro", f"Não foi possível gerar a comparação: {e}")

class AdvancedSnapshotViewWindow(QDialog):
    def __init__(self, snapshot, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Visualização Avançada: {snapshot.tag}")
        self.setMinimumSize(900, 600)
        self.snapshot = snapshot
        self.tag = snapshot.tag

        # Main layout
        main_layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)

        # Left side: File Tree
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Ficheiros do Snapshot"])
        self.tree.setColumnCount(1)
        self.tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        left_layout.addWidget(self.tree)
        
        # Right side: Metadata and Description
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(5, 0, 5, 0)

        # Metadata
        meta_layout = QFormLayout()
        meta_layout.addRow(QLabel("<b>Nome:</b>"), QLabel(snapshot.internal_name))
        meta_layout.addRow(QLabel("<b>Tag:</b>"), QLabel(snapshot.tag))
        meta_layout.addRow(QLabel("<b>Tipo:</b>"), QLabel(snapshot.type))
        meta_layout.addRow(QLabel("<b>Data:</b>"), QLabel(snapshot.date.strftime("%Y-%m-%d %H:%M:%S")))
        meta_layout.addRow(QLabel("<b>Mensagem:</b>"), QLabel(snapshot.message))
        
        right_layout.addLayout(meta_layout)

        # Description Area
        description_layout = QHBoxLayout()
        description_layout.addWidget(QLabel("<b>Descrição (Markdown):</b>"))
        description_layout.addStretch()
        self.edit_button = QPushButton("Editar")
        set_tooltip_if_enabled(self.edit_button, "Alternar entre visualização e edição da descrição.")
        self.edit_button.setCheckable(True)
        description_layout.addWidget(self.edit_button)
        right_layout.addLayout(description_layout)

        self.description_stack = QStackedWidget()
        self.description_viewer = QTextBrowser()
        self.description_viewer.setOpenExternalLinks(True)
        self.description_editor = QTextEdit()
        self.description_stack.addWidget(self.description_viewer)
        self.description_stack.addWidget(self.description_editor)
        right_layout.addWidget(self.description_stack)

        self.update_description_view()

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([350, 550]) 

        main_layout.addWidget(splitter)
        
        self.tree.itemDoubleClicked.connect(self.handle_double_click)
        self.edit_button.clicked.connect(self.toggle_edit_mode)
        
        self.load_tree(snapshot.tag)

    def update_description_view(self):
        self.description_viewer.setHtml(markdown2.markdown(self.snapshot.description or "<i>Sem descrição.</i>", extras=["fenced-code-blocks", "tables"]))

    def toggle_edit_mode(self, checked):
        if checked:
            self.edit_button.setText("Guardar e Ver")
            self.description_editor.setText(self.snapshot.description)
            self.description_stack.setCurrentWidget(self.description_editor)
        else:
            self.edit_button.setText("Editar")
            new_description = self.description_editor.toPlainText()
            if new_description != self.snapshot.description:
                try:
                    snapshots.update_snapshot_metadata(tag=self.tag, new_description=new_description)
                    self.snapshot.description = new_description
                    if self.parent() and hasattr(self.parent(), "status_label"):
                        self.parent().status_label.setText(f"Descrição do snapshot '{self.tag}' atualizada.")
                except GitSnapError as e:
                    QMessageBox.critical(self, "Erro", f"Não foi possível guardar a descrição: {e}")
                    # Revert button state if save failed
                    self.edit_button.setChecked(True)
                    self.edit_button.setText("Guardar e Ver")
                    return

            self.update_description_view()
            self.description_stack.setCurrentWidget(self.description_viewer)

    def _open_temp_snapshot_file(self, tag: str, file_path: str):
        """Helper para extrair e abrir um ficheiro de um snapshot."""
        try:
            content = snapshots.get_file_content_from_snapshot(tag, file_path)
            if content is None:
                QMessageBox.critical(self, "Erro", f"Ficheiro '{file_path}' não encontrado no snapshot '{tag}'.")
                return
            
            _, extension = os.path.splitext(file_path)
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=extension, encoding='utf-8') as tmp_file:
                tmp_file.write(content)
                tmp_file_path = tmp_file.name
            
            if self.parent() and hasattr(self.parent(), "status_label"):
                self.parent().status_label.setText(f"A abrir cópia temporária de '{file_path}' do snapshot '{tag}'...")
            
            open_file(tmp_file_path)
        except (GitSnapError, IOError) as e:
            QMessageBox.critical(self, "Erro", f"Não foi possível abrir o ficheiro temporário: {e}")

    def handle_double_click(self, item: QTreeWidgetItem):
        # Only open files, not directories
        if not item.childCount() > 0: # A simple way to check if it's a file
             file_path = item.data(0, Qt.UserRole)
             if file_path:
                self._open_temp_snapshot_file(self.tag, file_path)

    def load_tree(self, tag):
        try:
            items = snapshots.get_snapshot_tree(tag)
            self.populate_tree(items)
        except GitSnapError as e:
            QMessageBox.critical(self, "Erro", f"Não foi possível carregar a árvore de ficheiros: {e}")

    def populate_tree(self, items: list):
        self.tree.clear()
        nodes = {"": self.tree.invisibleRootItem()}
        for item in items:
            path = item['name']
            item_type = item['type'] # 'file' or 'dir'
            parts = path.split('/')
            parent_node = nodes[""]
            parent_path_key = ""
            for i, part in enumerate(parts[:-1]):
                parent_path_key = os.path.join(parent_path_key, part)
                if parent_path_key not in nodes:
                    parent_node = QTreeWidgetItem(parent_node, [part])
                    nodes[parent_path_key] = parent_node
                else:
                    parent_node = nodes[parent_path_key]
            
            node_item = QTreeWidgetItem(parent_node, [parts[-1]])
            # Store the full path in UserRole
            node_item.setData(0, Qt.UserRole, path)
            # If it's a directory, we don't set a specific role for opening
            if item_type == 'dir':
                node_item.setIcon(0, self.style().standardIcon(QStyle.SP_DirIcon))
            else:
                node_item.setIcon(0, self.style().standardIcon(QStyle.SP_FileIcon))
        self.tree.expandToDepth(0)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GitSnap")
        
        self.check_and_initialize_repo()

        self.setGeometry(100, 100, 800, 600)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 1. Create all widgets
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Pesquisar por nome ou tag...")
        
        self.filter_menu_button = QPushButton()
        self.filter_menu_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowDown))
        set_tooltip_if_enabled(self.filter_menu_button, "Opções de ordenação e filtro")

        self.help_button = QPushButton("Ajuda")
        set_tooltip_if_enabled(self.help_button, "Abrir documentação da aplicação.")
        self.settings_button = QPushButton("Configurações")
        set_tooltip_if_enabled(self.settings_button, "Configurar nome de utilizador, email e outras opções.")
        self.import_button = QPushButton("Importar")
        set_tooltip_if_enabled(self.import_button, "Importa um snapshot a partir de um ficheiro ZIP.")
        self.export_button = QPushButton("Exportar")
        set_tooltip_if_enabled(self.export_button, "Exporta um snapshot selecionado para um ficheiro ZIP.")

        self.status_label = QLabel("Bem-vindo")
        self.table = QTableWidget()
        
        self.create_button = QPushButton("Criar Snapshot")
        set_tooltip_if_enabled(self.create_button, "Guarda o estado atual de todos os ficheiros como um novo snapshot.")
        self.restore_button = QPushButton("Restaurar")
        set_tooltip_if_enabled(self.restore_button, "Reverte o projeto para o estado de um snapshot selecionado.")
        self.edit_button = QPushButton("Editar")
        set_tooltip_if_enabled(self.edit_button, "Edita o nome, tag, tipo e mensagem de um snapshot selecionado.")
        self.delete_button = QPushButton("Eliminar")
        set_tooltip_if_enabled(self.delete_button, "Apaga um snapshot permanentemente.")
        self.compare_local_button = QPushButton("Comparar com local")
        set_tooltip_if_enabled(self.compare_local_button, "Compara a snapshot selecionada com a versão local.")
        self.compare_two_button = QPushButton("Comparar com snapshot")
        set_tooltip_if_enabled(self.compare_two_button, "Compara duas snapshots diferentes.")
        self.push_button = QPushButton("Push para o GitHub")
        set_tooltip_if_enabled(self.push_button, "Abre a janela para enviar snapshots para o GitHub.")
        self.pull_button = QPushButton("Pull do GitHub")
        set_tooltip_if_enabled(self.pull_button, "Puxa as alterações mais recentes do repositório no GitHub.")

        # 2. Create layouts
        self.layout = QVBoxLayout(self.central_widget)
        top_layout = QHBoxLayout()
        button_layout = QHBoxLayout()
        compare_layout = QHBoxLayout()
        remote_layout = QHBoxLayout()

        # 3. Add widgets to layouts
        top_layout.addWidget(self.search_input, 1) # Add with stretch factor
        top_layout.addWidget(self.filter_menu_button)
        top_layout.addWidget(self.import_button)
        top_layout.addWidget(self.export_button)
        top_layout.addWidget(self.help_button)
        top_layout.addWidget(self.settings_button)
        
        button_layout.addWidget(self.restore_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        
        compare_layout.addWidget(self.compare_local_button)
        compare_layout.addWidget(self.compare_two_button)

        remote_layout.addWidget(self.pull_button)
        remote_layout.addWidget(self.push_button)
        
        # 4. Add layouts to main layout
        self.layout.addLayout(top_layout)
        self.layout.addWidget(self.table)
        self.layout.addWidget(self.create_button)
        self.layout.addLayout(button_layout)
        self.layout.addLayout(remote_layout)
        self.layout.addLayout(compare_layout)
        self.layout.addWidget(self.status_label)
        
        # 5. Connect signals
        self.setup_table()
        self.create_button.clicked.connect(self.create_snapshot)
        self.restore_button.clicked.connect(self.restore_snapshot)
        self.edit_button.clicked.connect(self.edit_snapshot)
        self.delete_button.clicked.connect(self.delete_snapshot)
        self.compare_local_button.clicked.connect(self.open_local_comparison_window)
        self.compare_two_button.clicked.connect(self.open_two_snapshot_comparison_window)
        self.import_button.clicked.connect(self.import_snapshot)
        self.export_button.clicked.connect(self.export_snapshot)
        self.settings_button.clicked.connect(self.open_settings_dialog)
        self.help_button.clicked.connect(self.open_help_dialog)
        self.push_button.clicked.connect(self.open_push_snapshot_dialog)
        self.pull_button.clicked.connect(self.open_pull_dialog)
        self.filter_menu_button.clicked.connect(self.open_filter_dialog)
        self.table.itemDoubleClicked.connect(self.open_snapshot_view_window)
        self.search_input.textChanged.connect(self.filter_and_sort_snapshots)
        
        # 6. Initial data load
        self.current_sort_option = "Data (mais recente)"
        self.current_type_filter = "Todos os Tipos"
        self.all_snapshots = []
        self.load_snapshots()

    def check_and_initialize_repo(self):
        try:
            git_repo.check_repo_ready()
        except RepositoryNotInitializedError as e:
            reply = QMessageBox.question(self, "Repositório Git Não Encontrado", f"{e}\n\nDeseja inicializar um novo repositório Git neste diretório?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    git_repo.initialize_and_setup_repo()
                    QMessageBox.information(self, "Sucesso", "Repositório Git inicializado com sucesso e pronto para uso.")
                except GitSnapError as init_e:
                    raise RuntimeError(f"Não foi possível inicializar o repositório:\n{init_e}") from init_e
            else:
                raise RuntimeError("O GitSnap não pode funcionar sem um repositório Git.")
        except GitSnapError as e:
            raise RuntimeError(f"Ocorreu um erro de Git inesperado:\n{e}") from e

    def open_pull_dialog(self):
        dialog = PullDialog(self)
        if dialog.exec(): self.load_snapshots()

    def open_push_snapshot_dialog(self):
        dialog = PushSnapshotDialog(self)
        if dialog.exec(): self.load_snapshots()

    def open_settings_dialog(self):
        dialog = SettingsDialog(self)
        dialog.exec()

    def open_help_dialog(self):
        dialog = HelpDialog(self)
        dialog.exec()

    def setup_table(self):
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Nome", "Tag", "Tipo", "Data", "Mensagem"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def load_snapshots(self):
        try:
            self.all_snapshots = snapshots.list_snapshots()
            self.filter_and_sort_snapshots()
        except GitSnapError as e:
            self.show_error_message(f"Erro ao carregar snapshots: {e}")

    def filter_and_sort_snapshots(self):
        search_text = self.search_input.text().lower()
        sort_option = self.current_sort_option
        type_filter = self.current_type_filter

        # 1. Filter by type
        if type_filter == "Todos os Tipos":
            filtered_snapshots = self.all_snapshots
        else:
            filtered_snapshots = [s for s in self.all_snapshots if s.type == type_filter]

        # 2. Filter by search text
        if search_text:
            filtered_snapshots = [
                s for s in filtered_snapshots
                if search_text in s.internal_name.lower() or
                   search_text in s.tag.lower()
            ]

        # 3. Sort the results
        if sort_option == "Data (mais recente)":
            filtered_snapshots.sort(key=lambda s: s.date, reverse=True)
        elif sort_option == "Data (mais antigo)":
            filtered_snapshots.sort(key=lambda s: s.date)
        elif sort_option == "Nome interno (A-Z)":
            filtered_snapshots.sort(key=lambda s: s.internal_name.lower())
        elif sort_option == "Tag (A-Z)":
            filtered_snapshots.sort(key=lambda s: s.tag.lower())
        elif sort_option == "Tipo (A-Z)":
            filtered_snapshots.sort(key=lambda s: s.type.lower())

        self.populate_table(filtered_snapshots)

    def open_filter_dialog(self):
        sort_options = ["Data (mais recente)", "Data (mais antigo)", "Nome interno (A-Z)", "Tag (A-Z)", "Tipo (A-Z)"]
        type_options = sorted(list({s.type for s in self.all_snapshots if s.type != "none"}))
        
        dialog = FilterSortDialog(sort_options, type_options, self.current_sort_option, self.current_type_filter, self)
        
        if dialog.exec():
            sort_option, filter_option = dialog.get_values()
            self._set_sort_by(sort_option)
            self._set_filter_by(filter_option)

    def _set_sort_by(self, sort_option):
        self.current_sort_option = sort_option
        self.filter_and_sort_snapshots()

    def _set_filter_by(self, type_filter):
        self.current_type_filter = type_filter
        self.filter_and_sort_snapshots()


    def populate_table(self, snaps):
        self.table.setRowCount(0)
        for row, snap in enumerate(snaps):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(snap.internal_name))
            self.table.setItem(row, 1, QTableWidgetItem(snap.tag))
            self.table.setItem(row, 2, QTableWidgetItem(snap.type))
            self.table.setItem(row, 3, QTableWidgetItem(snap.date.strftime("%Y-%m-%d %H:%M")))
            self.table.setItem(row, 4, QTableWidgetItem(snap.message))
        self.status_label.setText(f"{len(snaps)} snapshots encontrados.")

    def open_snapshot_view_window(self, item):
        tag = self.table.item(item.row(), 1).text()
        
        selected_snapshot = next((s for s in self.all_snapshots if s.tag == tag), None)
        if not selected_snapshot:
            return self.show_error_message("Não foi possível encontrar os detalhes do snapshot para visualização.")

        dialog = AdvancedSnapshotViewWindow(selected_snapshot, self)
        dialog.exec()

    def open_local_comparison_window(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if len(selected_rows) != 1:
            self.show_error_message("Por favor, selecione um único snapshot para comparar.")
            return
        tag = self.table.item(selected_rows[0].row(), 1).text()
        dialog = LocalComparisonWindow(tag, self); dialog.exec()


    def open_two_snapshot_comparison_window(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if len(selected_rows) != 2:
            self.show_error_message("Por favor, selecione exatamente dois snapshots para comparar.")
            return
        tag1 = self.table.item(selected_rows[0].row(), 1).text()
        tag2 = self.table.item(selected_rows[1].row(), 1).text()
        dialog = TwoSnapshotComparisonWindow(tag1, tag2, self); dialog.exec()

    def create_snapshot(self):
        existing_types = {s.type for s in self.all_snapshots if s.type != "none"}
        dialog = CreateSnapshotDialog(self, existing_types=existing_types)
        if dialog.exec():
            internal_name, tag, message, snapshot_type, description = dialog.get_values()
            if internal_name and tag and message:
                try:
                    snapshots.save_snapshot(internal_name, tag, message, snapshot_type, description)
                    self.load_snapshots()
                    self.status_label.setText("Snapshot criado com sucesso!")
                except (NoChangesError, GitSnapError, ValueError) as e:
                    self.show_error_message(f"Erro: {e}")
            else:
                self.show_error_message("Todos os campos são obrigatórios.")

    def restore_snapshot(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if len(selected_rows) != 1: return self.show_error_message("Por favor, selecione um único snapshot.")
        tag = self.table.item(selected_rows[0].row(), 1).text()
        if QMessageBox.question(self, "Confirmar", f"Tem a certeza que quer restaurar o snapshot '{tag}'? Todas as alterações não guardadas serão perdidas.", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            try:
                snapshots.restore_snapshot(tag)
                self.load_snapshots()
                self.status_label.setText(f"Snapshot '{tag}' restaurado com sucesso.")
                QMessageBox.information(self, "Sucesso", f"Snapshot '{tag}' restaurado com sucesso.")
            except GitSnapError as e: self.show_error_message(f"Erro ao restaurar: {e}")

    def edit_snapshot(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if len(selected_rows) != 1: return self.show_error_message("Por favor, selecione um único snapshot para editar.")
        row = selected_rows[0].row()
        
        # Find the full snapshot object to get the description
        tag_to_find = self.table.item(row, 1).text()
        selected_snapshot = next((s for s in self.all_snapshots if s.tag == tag_to_find), None)
        if not selected_snapshot:
            return self.show_error_message("Não foi possível encontrar os detalhes do snapshot selecionado.")

        old_internal_name = selected_snapshot.internal_name
        old_tag = selected_snapshot.tag
        old_type = selected_snapshot.type
        old_message = selected_snapshot.message
        old_description = selected_snapshot.description
        
        existing_types = {s.type for s in self.all_snapshots if s.type != "none"}
        
        dialog = EditSnapshotDialog(old_internal_name, old_tag, old_message, old_type, old_description, existing_types, self)
        if dialog.exec():
            new_internal_name, new_tag, new_message, new_type, new_description = dialog.get_values()
            try:
                tag_to_update = old_tag
                
                if new_internal_name != old_internal_name or new_type != old_type or new_description != old_description:
                    snapshots.update_snapshot_metadata(tag_to_update, new_internal_name, new_type, new_description)

                if new_tag != old_tag:
                    snapshots.rename_snapshot_tag(old_tag, new_tag)
                    tag_to_update = new_tag
                
                if new_message != old_message:
                    snapshots.rename_snapshot(tag_to_update, new_message)
                
                self.load_snapshots()
                self.status_label.setText(f"Snapshot '{old_tag}' editado com sucesso.")
            except (GitSnapError, ValueError) as e: self.show_error_message(f"Erro ao editar: {e}")

    def delete_snapshot(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return self.show_error_message("Por favor, selecione um ou mais snapshots para eliminar.")
        
        tags_to_delete = [self.table.item(row.row(), 1).text() for row in selected_rows]
        
        if len(tags_to_delete) == 1:
            question = f"Tem a certeza que quer eliminar o snapshot '{tags_to_delete[0]}'? Esta ação não pode ser desfeita."
        else:
            question = f"Tem a certeza que quer eliminar os {len(tags_to_delete)} snapshots selecionados? Esta ação não pode ser desfeita."

        if QMessageBox.question(self, "Confirmar Eliminação", question, QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            try:
                for tag in tags_to_delete:
                    snapshots.delete_snapshot(tag)
                
                self.load_snapshots()
                
                if len(tags_to_delete) == 1:
                    self.status_label.setText(f"Snapshot '{tags_to_delete[0]}' eliminado com sucesso.")
                else:
                    self.status_label.setText(f"{len(tags_to_delete)} snapshots eliminados com sucesso.")
            except GitSnapError as e:
                self.show_error_message(f"Erro ao eliminar snapshots: {e}")

    def export_snapshot(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if len(selected_rows) != 1:
            return self.show_error_message("Por favor, selecione um único snapshot para exportar.")
        
        row = selected_rows[0].row()
        tag = self.table.item(row, 1).text()
        
        default_filename = f"{tag}.zip"
        export_path, _ = QFileDialog.getSaveFileName(self, "Exportar Snapshot", default_filename, "ZIP Files (*.zip)")
        
        if not export_path:
            return

        try:
            snapshots.export_snapshot(tag, export_path)
            self.status_label.setText(f"Snapshot '{tag}' exportado com sucesso para '{export_path}'.")
            QMessageBox.information(self, "Sucesso", f"Snapshot '{tag}' exportado com sucesso.")
        except GitSnapError as e:
            self.show_error_message(f"Erro ao exportar snapshot: {e}")

    def import_snapshot(self):
        import_path, _ = QFileDialog.getOpenFileName(self, "Importar Snapshot", "", "ZIP Files (*.zip)")
        
        if not import_path:
            return

        try:
            snapshots.import_snapshot(import_path)
            self.load_snapshots()
            self.status_label.setText("Snapshot importado com sucesso!")
            QMessageBox.information(self, "Sucesso", "Snapshot importado e adicionado à lista com sucesso.")
        except GitSnapError as e:
            self.show_error_message(f"Erro ao importar snapshot: {e}")

    def show_error_message(self, message: str):
        self.status_label.setText(message); QMessageBox.critical(self, "Erro", message)

def run_gui():
    try:
        app = QApplication(sys.argv)
        
        window = MainWindow()
        window.show()
        sys.exit(app.exec())

    except Exception as e:
        print(f"ERRO FATAL AO INICIAR A APLICAÇÃO: {e.__class__.__name__}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_gui()
import os

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QSplitter, QListWidget, QWidget, QMessageBox, QInputDialog, QMenu
from PySide6.QtCore import Qt

from src.widget.markdown_editor import MarkdownEditor


class DiaryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Markdown 日记应用")
        self.resize(800, 600)

        self.current_file = None  # 当前打开的日记文件
        self.preview_mode = False  # 当前是否为预览模式
        self.init_ui()

    def init_ui(self):
        # 主分割器
        self.splitter = QSplitter(Qt.Horizontal, self)
        self.setCentralWidget(self.splitter)

        # 左侧：日记列表
        self.diary_list = QListWidget(self)
        self.diary_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.diary_list.customContextMenuRequested.connect(self.show_context_menu)
        self.diary_list.itemClicked.connect(self.load_diary)
        self.splitter.addWidget(self.diary_list)

        # 右侧：Markdown 编辑器
        self.markdown_editor = MarkdownEditor()  # 使用新的Markdown编辑器模块
        self.splitter.addWidget(self.markdown_editor)

        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 3)

        # 加载日记列表
        self.load_diary_list()

    def load_diary_list(self):
        """加载日记列表"""
        self.diary_list.clear()
        if not os.path.exists("diaries"):
            os.makedirs("diaries")
        for file_name in os.listdir("diaries"):
            if file_name.endswith(".md"):
                self.diary_list.addItem(file_name[:-3])

    def load_diary(self, item):
        """加载选中的日记"""
        file_name = item.text()
        file_path = f"diaries/{file_name}.md"

        if not os.path.exists(file_path):
            QMessageBox.warning(self, "警告", f"文件不存在：{file_name}")
            return

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                self.markdown_editor.set_content(content)
                self.current_file = file_name
                if self.preview_mode:
                    self.markdown_editor.switch_to_preview()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载日记失败：{str(e)}")

    def auto_save(self):
        """切换日记时自动保存"""
        if self.current_file:
            file_path = f"diaries/{self.current_file}.md"
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(self.markdown_editor.get_content())
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存日记失败：{str(e)}")

    def show_context_menu(self, position):
        """显示右键菜单"""
        menu = QMenu()

        delete_action = QAction("删除日记", self)
        delete_action.triggered.connect(self.delete_diary)
        menu.addAction(delete_action)

        rename_action = QAction("重命名日记", self)
        rename_action.triggered.connect(self.rename_diary)
        menu.addAction(rename_action)

        menu.exec(self.diary_list.viewport().mapToGlobal(position))

    def delete_diary(self):
        """删除选中的日记"""
        current_item = self.diary_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择要删除的日记！")
            return

        reply = QMessageBox.question(
            self, "确认删除", f"确定要删除日记 '{current_item.text()}' 吗？",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            file_name = current_item.text()
            file_path = f"diaries/{file_name}.md"
            if os.path.exists(file_path):
                os.remove(file_path)
            self.diary_list.takeItem(self.diary_list.row(current_item))
            if self.current_file == file_name:
                self.current_file = None
                self.markdown_editor.set_content("")
            QMessageBox.information(self, "成功", f"已删除日记：{file_name}")

    def rename_diary(self):
        """重命名选中的日记"""
        current_item = self.diary_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择要重命名的日记！")
            return

        old_name = current_item.text()
        new_name, ok = QInputDialog.getText(self, "重命名日记", "请输入新的日记名称：", text=old_name)
        if not ok or not new_name:
            return

        old_file_path = f"diaries/{old_name}.md"
        new_file_path = f"diaries/{new_name}.md"

        if os.path.exists(new_file_path):
            QMessageBox.warning(self, "警告", "同名文件已存在！")
            return

        try:
            os.rename(old_file_path, new_file_path)
            current_item.setText(new_name)
            if self.current_file == old_name:
                self.current_file = new_name
        except Exception as e:
            QMessageBox.critical(self, "错误", f"重命名失败：{str(e)}")


if __name__ == "__main__":
    app = QApplication([])
    window = DiaryApp()
    window.show()
    app.exec()

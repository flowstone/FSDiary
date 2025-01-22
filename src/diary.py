from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QListWidget, \
    QMessageBox, QInputDialog, QWidget, QMenu
from PySide6.QtCore import Qt, QTimer
import os
from loguru import logger
from src.util.common_util import CommonUtil
from src.util.encryption_util import EncryptionUtil
from src.util.message_util import MessageUtil

DIARY_DIR = f"{CommonUtil.get_diary_enc_path()}"

class DiaryApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("日记应用")

        # 加载加密密钥
        self.key = self.load_key()
        if not self.key:
            MessageUtil.show_error_message("无法加载密钥文件！")
            exit()

        # 当前日记文件
        self.current_file = None

        # 保存延迟计时器
        self.save_timer = QTimer()
        self.save_timer.setInterval(2000)  # 2 秒延迟
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self.auto_save)

        self.init_ui()

    def init_ui(self):
        # 主界面布局
        main_layout = QHBoxLayout()
        # 左侧布局（按钮 + 列表）
        left_layout = QVBoxLayout()

        # 新建日记按钮
        add_button = QPushButton("新建日记")
        add_button.clicked.connect(self.new_diary)
        left_layout.addWidget(add_button)
        # 左侧列表
        self.diary_list = QListWidget()
        self.diary_list.itemClicked.connect(self.load_diary)
        self.diary_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.diary_list.customContextMenuRequested.connect(self.show_context_menu)
        left_layout.addWidget(self.diary_list)
        main_layout.addLayout(left_layout, 2)

        # 右侧编辑框
        self.diary_content = QTextEdit()
        self.diary_content.textChanged.connect(self.start_save_timer)  # 监听文本修改
        main_layout.addWidget(self.diary_content, 5)


        self.setLayout(main_layout)

        self.load_diary_list()

    def show_context_menu(self, position):
        """显示右键菜单"""
        menu = QMenu()

        # 添加删除选项
        delete_action = QAction("删除日记", self)
        delete_action.triggered.connect(self.delete_diary)
        menu.addAction(delete_action)

        # 重命名选项
        rename_action = QAction("重命名日记", self)
        rename_action.triggered.connect(self.rename_diary)
        menu.addAction(rename_action)

        # 在列表中显示右键菜单
        menu.exec(self.diary_list.viewport().mapToGlobal(position))

    def start_save_timer(self):
        """在用户输入时启动保存计时器"""
        if self.current_file:  # 只有选择了日记才进行保存
            self.save_timer.start()

    def auto_save(self):
        """自动保存日记"""
        if not self.current_file:
            return
        content = self.diary_content.toPlainText()
        file_path = f"{DIARY_DIR}/{self.current_file}.enc"

        try:
            encrypted_data = EncryptionUtil.encrypt(content.encode(), self.key)
            with open(file_path, "wb") as file:
                file.write(encrypted_data)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"自动保存失败：{str(e)}")

    @staticmethod
    def load_key():
        key_file = CommonUtil.get_diary_key_path()
        if  os.path.exists(key_file):
            with open(key_file, "rb") as file:
                return file.read()


    def load_diary_list(self):
        self.diary_list.clear()
        diaries_path = CommonUtil.get_diary_enc_path()
        for file_name in os.listdir(diaries_path):
            if file_name.endswith(".enc"):
                self.diary_list.addItem(file_name[:-4])

    def load_diary(self, item):
        """加载选中的日记"""
        # 自动保存当前日记内容
        if self.current_file:
            self.auto_save()

        # 获取选中的日记文件名
        self.current_file = item.text()
        file_path = f"{DIARY_DIR}/{self.current_file}.enc"

        # 检查文件是否存在
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "警告", f"日记文件不存在：{file_path}")
            self.diary_list.takeItem(self.diary_list.row(item))
            self.current_file = None
            return

        # 加载并显示日记内容
        try:
            with open(file_path, "rb") as file:
                encrypted_data = file.read()
                content = EncryptionUtil.decrypt(encrypted_data, self.key).decode()
                self.diary_content.setPlainText(content)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法加载日记：{str(e)}")
            self.diary_list.takeItem(self.diary_list.row(item))
            self.current_file = None

    def new_diary(self):
        """新建日记"""
        file_name, ok = QInputDialog.getText(self, "新建日记", "请输入日记标题：")
        if ok and file_name:
            self.current_file = file_name
            file_path = f"{DIARY_DIR}/{self.current_file}.enc"

            # 如果文件已存在，提示用户选择其他名称
            if os.path.exists(file_path):
                QMessageBox.warning(self, "警告", "同名日记已存在，请使用其他名称。")
                return
            # 创建一个空的加密文件
            try:
                encrypted_data = EncryptionUtil.encrypt("".encode(), self.key)
                with open(file_path, "wb") as file:
                    file.write(encrypted_data)

            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法创建新日记文件：{str(e)}")
                return

            self.diary_list.addItem(self.current_file)

            self.diary_content.clear()
            QMessageBox.information(self, "成功", f"已创建新日记：{file_name}")

    def save_diary(self):
        content = self.diary_content.toPlainText()
        if not content:
            QMessageBox.warning(self, "警告", "日记内容不能为空！")
            return
        file_name, ok = QInputDialog.getText(self, "保存日记", "请输入日记标题：")
        if ok and file_name:
            try:
                encrypted_data = EncryptionUtil.encrypt(content.encode(), self.key)
                with open(f"{DIARY_DIR}/{file_name}.enc", "wb") as file:
                    file.write(encrypted_data)
                self.load_diary_list()
                QMessageBox.information(self, "成功", "日记已保存！")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法保存日记：{str(e)}")

    def delete_diary(self):
        """删除日记"""
        selected_item = self.diary_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "警告", "请先选择一篇日记！")
            return
        # 确认是否删除
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除日记 '{selected_item.text()}' 吗？",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            file_name = selected_item.text()
            file_path = f"{DIARY_DIR}/{file_name}.enc"

            # 删除文件
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    QMessageBox.information(self, "成功", f"已删除日记：{file_name}")
                else:
                    QMessageBox.warning(self, "警告", f"文件不存在：{file_path}")

                # 从列表中移除对应项
                self.diary_list.takeItem(self.diary_list.row(selected_item))

                # 如果删除的是当前日记，清空编辑框
                if self.current_file == file_name:
                    self.current_file = None
                    self.diary_content.clear()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除日记失败：{str(e)}")

    def rename_diary(self):
        """重命名选中的日记"""
        # 获取当前选中的列表项
        current_item = self.diary_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择要重命名的日记！")
            return

        old_name = current_item.text()
        old_file_path = f"{DIARY_DIR}/{old_name}.enc"

        # 输入新的文件名
        new_name, ok = QInputDialog.getText(self, "重命名日记", "请输入新的日记名称：", text=old_name)
        if not ok or not new_name:
            return  # 用户取消操作或输入为空

        # 检查是否重名
        new_file_path = f"{DIARY_DIR}/{new_name}.enc"
        if os.path.exists(new_file_path):
            QMessageBox.warning(self, "警告", "文件名已存在，请使用其他名称。")
            return

        # 重命名文件
        try:
            os.rename(old_file_path, new_file_path)

            # 更新列表项显示名称
            current_item.setText(new_name)

            # 如果重命名的是当前正在编辑的文件，更新 self.current_file
            if self.current_file == old_name:
                self.current_file = new_name

            QMessageBox.information(self, "成功", f"日记已重命名为：{new_name}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"重命名失败：{str(e)}")

if __name__ == "__main__":
    app = QApplication([])
    window = DiaryApp()
    window.show()
    app.exec()

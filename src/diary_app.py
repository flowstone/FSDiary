from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QListWidget, \
    QMessageBox, QInputDialog, QWidget, QMenu, QSplitter, QFileDialog, QAbstractItemView
from PySide6.QtCore import Qt, QTimer
import os
from loguru import logger

from src.const.fs_constants import FsConstants
from src.context_menu import DiaryContextMenu
from src.ui_components import UiComponents
from src.util.common_util import CommonUtil
from src.util.encryption_util import EncryptionUtil
from src.util.message_util import MessageUtil
from src.widget.markdown_editor import MarkdownEditor
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

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
        self.menu = None
        # 保存延迟计时器
        self.save_timer = QTimer()
        self.save_timer.setInterval(10000)  # 2 秒延迟
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self.auto_save)

        self.init_ui()

    def init_ui(self):
        # 主界面布局
        main_layout = QHBoxLayout()
        # 使用封装的布局类
        self.diary_layout = UiComponents()
        add_button = self.diary_layout.add_button
        self.diary_list = self.diary_layout.diary_list
        self.diary_content = self.diary_layout.diary_content

        add_button.clicked.connect(self.new_diary)
        add_button.clicked.connect(self.new_diary)
        self.diary_list.itemClicked.connect(self.load_diary)
        self.diary_list.customContextMenuRequested.connect(self.show_context_menu)
        self.diary_content.textChanged.connect(self.start_save_timer)  # 监听文本修改


        main_layout.addWidget(self.diary_layout)
        self.setLayout(main_layout)
        self.load_diary_list()

        self.diary_list.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

    def show_context_menu(self, position):
         """显示右键菜单"""
         # 防止menu对象销毁，信号槽绑定失效
         if not hasattr(self, 'menu') or self.menu is None:
             self.menu = DiaryContextMenu(self, self.diary_list, self.diary_content, self.current_file, self.key, DIARY_DIR)
             self.menu.current_file_deleted.connect(self.update_external_current_file)

         self.menu.exec(self.diary_list.viewport().mapToGlobal(position))

    def update_external_current_file(self):
        self.current_file = None

    def start_save_timer(self):
        """在用户输入时启动保存计时器"""
        if self.current_file:  # 只有选择了日记才进行保存
            self.save_timer.start()

    def auto_save(self):
        """自动保存日记"""
        if not self.current_file:
            return
        content = self.diary_content.get_content()
        file_path = f"{DIARY_DIR}/{self.current_file}.enc"

        try:
            encrypted_data = EncryptionUtil.encrypt(content.encode(), self.key)
            with open(file_path, "wb") as file:
                file.write(encrypted_data)
        except Exception as e:
            MessageUtil.show_error_message(f"自动保存失败：{str(e)}")

    @staticmethod
    def load_key():
        key_file = CommonUtil.get_diary_key_path()
        if  os.path.exists(key_file):
            with open(key_file, "rb") as file:
                return file.read()


    def load_diary_list(self):
        """加载日记列表并按修改时间倒序排序"""
        self.diary_list.clear()
        diaries_path = CommonUtil.get_diary_enc_path()

        # 获取所有 .enc 文件及其修改时间
        diaries = [
            (file_name[:-4], os.path.getmtime(os.path.join(diaries_path, file_name)))
            for file_name in os.listdir(diaries_path)
            if file_name.endswith(".enc")
        ]

        # 按修改时间倒序排序
        diaries.sort(key=lambda x: x[1], reverse=True)

        # 添加到列表
        for file_name, _ in diaries:
            self.diary_list.addItem(file_name)

        # 默认选择第一个日记并加载内容
        if self.diary_list.count() > 0:
            first_item = self.diary_list.item(0)
            self.diary_list.setCurrentItem(first_item)
            self.load_diary(first_item)


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
            MessageUtil.show_warning_message(f"日记文件不存在：{file_path}")
            self.diary_list.takeItem(self.diary_list.row(item))
            self.current_file = None
            return


        # 如果 Markdown 编辑器在预览模式，切换回编辑模式
        if self.diary_content.is_preview_mode():
            self.diary_content.switch_to_edit()


        # 加载并显示日记内容
        try:
            with open(file_path, "rb") as file:
                encrypted_data = file.read()
                content = EncryptionUtil.decrypt(encrypted_data, self.key).decode()
                self.diary_content.set_content(content)
        except Exception as e:
            MessageUtil.show_error_message(f"无法加载日记：{str(e)}")
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
                MessageUtil.show_warning_message("同名日记已存在，请使用其他名称。")
                return

            # 创建一个空的加密文件
            try:
                encrypted_data = EncryptionUtil.encrypt("".encode(), self.key)
                with open(file_path, "wb") as file:
                    file.write(encrypted_data)

            except Exception as e:
                MessageUtil.show_error_message(f"无法创建新日记文件：{str(e)}")
                return

            # 重新加载列表（新建的文件会自动排在第一位）
            self.load_diary_list()

            # 自动选中新建条目
            first_item = self.diary_list.item(0)
            self.diary_list.setCurrentItem(first_item)
            self.diary_content.clear_content()

            MessageUtil.show_success_message(f"已创建新日记：{file_name}")

    def save_diary(self):
        content = self.diary_content.get_content()
        if not content:
            MessageUtil.show_warning_message("日记内容不能为空！")
            return
        file_name, ok = QInputDialog.getText(self, "保存日记", "请输入日记标题：")
        if ok and file_name:
            try:
                encrypted_data = EncryptionUtil.encrypt(content.encode(), self.key)
                with open(f"{DIARY_DIR}/{file_name}.enc", "wb") as file:
                    file.write(encrypted_data)
                self.load_diary_list()
                MessageUtil.show_success_message("日记已保存！")
            except Exception as e:
                MessageUtil.show_error_message(f"无法保存日记：{str(e)}")


    def closeEvent(self, event):
        self.auto_save()
        # 调用父类关闭事件
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication([])
    window = DiaryApp()
    window.show()
    app.exec()

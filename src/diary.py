from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QListWidget, \
    QMessageBox, QInputDialog, QWidget
from PySide6.QtCore import Qt
import os

from src.util.common_util import CommonUtil
from src.util.encryption_util import EncryptionUtil
from src.util.message_util import MessageUtil


class DiaryApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("日记应用")

        # 加载加密密钥
        self.key = self.load_key()
        if not self.key:
            MessageUtil.show_error_message("无法加载密钥文件！")
            exit()

        self.init_ui()

    def init_ui(self):
        # 主界面布局
        main_layout = QHBoxLayout()

        # 左侧列表
        self.diary_list = QListWidget()
        self.diary_list.itemClicked.connect(self.load_diary)
        main_layout.addWidget(self.diary_list, 2)

        # 右侧编辑框
        self.diary_content = QTextEdit()
        main_layout.addWidget(self.diary_content, 5)

        # 下方按钮
        button_layout = QVBoxLayout()
        add_button = QPushButton("新建日记")
        add_button.clicked.connect(self.new_diary)
        save_button = QPushButton("保存日记")
        save_button.clicked.connect(self.save_diary)
        delete_button = QPushButton("删除日记")
        delete_button.clicked.connect(self.delete_diary)

        button_layout.addWidget(add_button)
        button_layout.addWidget(save_button)
        button_layout.addWidget(delete_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout, 1)
        self.setLayout(main_layout)

        self.load_diary_list()

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
        file_name = f"{CommonUtil.get_diary_enc_path()}/{item.text()}.enc"
        try:
            with open(file_name, "rb") as file:
                encrypted_data = file.read()
                content = EncryptionUtil.decrypt(encrypted_data, self.key).decode()
                self.diary_content.setPlainText(content)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法加载日记：{str(e)}")

    def new_diary(self):
        self.diary_content.clear()

    def save_diary(self):
        content = self.diary_content.toPlainText()
        if not content:
            QMessageBox.warning(self, "警告", "日记内容不能为空！")
            return
        file_name, ok = QInputDialog.getText(self, "保存日记", "请输入日记标题：")
        if ok and file_name:
            try:
                encrypted_data = EncryptionUtil.encrypt(content.encode(), self.key)
                with open(f"{CommonUtil.get_diary_enc_path()}/{file_name}.enc", "wb") as file:
                    file.write(encrypted_data)
                self.load_diary_list()
                QMessageBox.information(self, "成功", "日记已保存！")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法保存日记：{str(e)}")

    def delete_diary(self):
        selected_item = self.diary_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "警告", "请先选择一篇日记！")
            return
        file_name = f"{CommonUtil.get_diary_enc_path()}/{selected_item.text()}.enc"
        if os.path.exists(file_name):
            os.remove(file_name)
            self.load_diary_list()
            QMessageBox.information(self, "成功", "日记已删除！")

if __name__ == "__main__":
    app = QApplication([])
    window = DiaryApp()
    window.show()
    app.exec()

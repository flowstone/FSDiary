#显示通用消息框
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QLabel, QPushButton, QTextEdit
from PySide6.QtCore import Qt
from loguru import logger

from src.util.common_util import CommonUtil


class MessageUtil:
    @staticmethod
    def show_success_message(message):
        MessageUtil.show_message("提示", message)

    @staticmethod
    def show_error_message(message):
        MessageUtil.show_message("错误", message, message_type="error")

    @staticmethod
    def show_warning_message(message):
        MessageUtil.show_message("警告", message, message_type="warning")

    @staticmethod
    def show_message(title, message, message_type="info", details=None, parent=None):
        """
        显示通用消息框。

        :param title: 消息框标题
        :param message: 主消息内容
        :param details: 可选，详细信息（如堆栈跟踪）
        :param message_type: 消息类型 ("info", "warning", "error")
        :param parent: 可选，父窗口
        """
        msg_box = QMessageBox(parent)

        # 设置图标和标题
        if message_type == "info":
            msg_box.setIcon(QMessageBox.Icon.Information)
        elif message_type == "warning":
            msg_box.setIcon(QMessageBox.Icon.Warning)
        elif message_type == "error":
            msg_box.setIcon(QMessageBox.Icon.Critical)
        else:
            msg_box.setIcon(QMessageBox.Icon.NoIcon)

        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setWindowIcon(QIcon(CommonUtil.get_ico_full_path()))
        # 添加详细信息按钮
        if details:
            msg_box.setDetailedText(details)

        # 设置按钮
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    #显示错误对话框，支持详细信息展开。
    @staticmethod
    def show_error_dialog(title, message, details=None, parent=None):
        """
        显示错误对话框，支持详细信息展开。

        :param title: 对话框标题
        :param message: 主消息内容
        :param details: 可选，详细信息
        :param parent: 可选，父窗口
        """
        dialog = QDialog(parent)
        dialog.setWindowTitle(title)
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        dialog.resize(400, 300)

        layout = QVBoxLayout(dialog)

        # 主消息
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)

        # 详细信息按钮
        if details:
            details_button = QPushButton("显示详细信息")
            details_button.setCheckable(True)
            layout.addWidget(details_button)

            details_area = QTextEdit(details)
            details_area.setReadOnly(True)
            details_area.setVisible(False)
            layout.addWidget(details_area)

            # 按钮控制详细信息显示
            def toggle_details():
                details_area.setVisible(details_button.isChecked())
                details_button.setText("隐藏详细信息" if details_button.isChecked() else "显示详细信息")

            details_button.clicked.connect(toggle_details)

        # 确定按钮
        close_button = QPushButton("关闭")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)

        dialog.exec()

    #显示错误消息框并自动记录日志
    @staticmethod
    def show_error_message_with_logging(title, message, details=None, parent=None):
        """
        显示错误消息框并自动记录日志。

        :param title: 消息框标题
        :param message: 主消息内容
        :param details: 可选，详细信息
        :param parent: 可选，父窗口
        """
        logger.error(f"{title}: {message}\n{details if details else ''}")
        MessageUtil.show_error_dialog(title, message, details, parent)

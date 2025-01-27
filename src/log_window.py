import sys
import platform
import tempfile
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMenuBar, QMenu, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QSystemTrayIcon, QMenu
from fs_base.widget import MenuWindow

from src.const.fs_constants import FsConstants
import os
from src.util.common_util import CommonUtil
from loguru import logger



class LogStream:
    """自定义日志流，将输出重定向到 QTextEdit"""

    def __init__(self, text_edit):
        self.text_edit = text_edit

    def write(self, message):
        """将信息写入 QTextEdit 控件"""
        if self.text_edit:
            # 根据日志级别设置颜色
            if "ERROR" in message:
                self.text_edit.setTextColor("red")  # 错误信息为红色
            elif "WARNING" in message:
                self.text_edit.setTextColor("orange")  # 警告信息为橙色
            else:
                self.text_edit.setTextColor("black")  # 普通信息为黑色

            self.text_edit.append(message.strip())  # 去掉多余换行符

    def flush(self):
        """flush 方法用于兼容 sys.stdout"""
        pass


class LogWindow(MenuWindow):
    """日志窗口类"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("日志窗口")
        logger.info(f"---- 初始化日志窗口 ----")
        self.setWindowIcon(QIcon(CommonUtil.get_ico_full_path()))

        self.setGeometry(0, 0, 800, 400)
        self.layout = QVBoxLayout(self)

        # 创建 QTextEdit 控件来显示日志
        self.log_text_edit = QTextEdit(self)
        self.log_text_edit.setReadOnly(True)

        self.layout.addWidget(self.log_text_edit)
        self.setLayout(self.layout)

        # 备份原始输出流
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

        # 将日志输出到 QTextEdit
        sys.stdout = LogStream(self.log_text_edit)
        sys.stderr = LogStream(self.log_text_edit)
        logger.add(sys.stdout, level="INFO")
        logger.add(sys.stdout, level="WARNING")
        logger.add(sys.stderr, level="ERROR")
        # 添加基础信息
        self.add_basic_info()

    @staticmethod
    def add_basic_info():
        """添加系统和环境基础信息"""
        logger.info("=== 系统与环境信息 ===")
        logger.info(f"操作系统: {platform.system()} {platform.release()}")
        logger.info(f"IP: {CommonUtil.get_local_ip()}")
        logger.info(f"资源目录: {CommonUtil.get_resource_path('')}")
        logger.info(f"外部目录: {CommonUtil.get_external_path()}")
        logger.info("===================")

    def closeEvent(self, event):
        """在窗口关闭时恢复标准输出和错误输出"""
        try:
            # 恢复标准输出流
            sys.stdout = self.original_stdout
            sys.stderr = self.original_stderr
        except Exception as e:
            logger.warning(f"关闭日志窗口时发生错误: {e}")
        self.hide()  # 隐藏窗口而不是销毁
        event.ignore()  # 忽略关闭事件

import os
import sys

from PySide6.QtCore import Signal, QObject
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QAction
from loguru import logger
from src.util.common_util import CommonUtil
from src.const.fs_constants import FsConstants
from src.util.config_util import ConfigUtil


class TrayMenu(QObject):
    show_main_signal = Signal()
    activated_signal = Signal(QSystemTrayIcon.ActivationReason)
    quit_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tray_icon = None

    def init_tray_menu(self, main_window):
        logger.info("---- 初始化任务栏图标 ----")
        # 创建系统托盘图标
        self.tray_icon = QSystemTrayIcon(main_window)
        self.tray_icon.setIcon(
            QIcon(ConfigUtil.get_ini_tray_menu_image()))  # 这里需要一个名为icon.png的图标文件，可以替换为真实路径
        # 双击托盘图标，打开主界面
        self.tray_icon.activated.connect(self.activate_signal_emit)

        # 创建托盘菜单
        try:
            tray_menu = QMenu()
            show_action = QAction("主界面", main_window)
            show_action.triggered.connect(self.show_main_signal_emit)
            restart_action = QAction("重启", main_window)
            restart_action.triggered.connect(self.restart_app)
            quit_action = QAction("退出", main_window)
            quit_action.triggered.connect(QApplication.quit)
            tray_menu.addAction(show_action)
            tray_menu.addAction(restart_action)
            tray_menu.addAction(quit_action)
            self.tray_icon.setContextMenu(tray_menu)
        except Exception as e:
            logger.error(f"托盘菜单初始化时发生异常: {e}")

    def activate_signal_emit(self, reason):
        try:
            self.activated_signal.emit(reason)
        except Exception as e:
            logger.error(f"托盘图标激活处理时发生异常: {e}")

    def show_main_signal_emit(self):
        self.show_main_signal.emit()


    # 重启应用
    @staticmethod
    def restart_app():
        # 获取当前脚本路径并重新启动应用
        logger.info("重启应用")
        python = sys.executable
        os.execl(python, python, *sys.argv)  # 重新启动当前应用
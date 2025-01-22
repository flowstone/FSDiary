import base64
import datetime
import sys
import uuid

import requests
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QSystemTrayIcon, QMenu, QMainWindow, QLabel, QTextEdit, \
    QFileDialog

from PySide6.QtGui import QIcon, Qt, QDragEnterEvent, QDropEvent

from src.image_tool import ImageToolApp
from src.util.config_util import ConfigUtil
from src.widget.app_mini import FloatingBall
from loguru import logger
from src.util.common_util import CommonUtil
from src.const.fs_constants import FsConstants
from src.util.menu_bar import MenuBar
from src.widget.tray_menu import TrayMenu


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.menubar = None
        self.floating_ball = FloatingBall(self)
        self.is_floating_ball_visible = False
        self.tray_menu = TrayMenu(self)
        self.init_ui()

    def init_ui(self):
        #self.setGeometry(300, 200, 600, 400)
        self.setWindowTitle(FsConstants.APP_WINDOW_TITLE)
        # 设置拖拽支持
        self.setAcceptDrops(True)
        logger.info(f"调用了主界面的初始化,悬浮球标志位 = {self.is_floating_ball_visible}")

        # ---- 工具栏 START
        self.menubar = MenuBar(self)
        # ---- 工具栏 END

        self.setWindowIcon(QIcon(CommonUtil.get_ico_full_path()))



        # 初始化应用托盘图标
        self.tray_menu.init_tray_menu(self)
        self.tray_menu.activated_signal.connect(self.tray_icon_activated)
        self.tray_menu.show_main_signal.connect(self.tray_menu_show_main)

        # 创建中央小部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        image_tool = ImageToolApp()

        main_layout.addWidget(image_tool)  # 将其添加到布局中

    # 从托盘菜单点击显示主界面
    def tray_menu_show_main(self):
        logger.info("---- 托盘菜单点击显示窗口 ----")
        # 悬浮球退出
        self.floating_ball.close()
        self.is_floating_ball_visible = False
        self.show()


    # 处理窗口关闭事件
    def handle_close_event(self, event):
        logger.info(f"开始关闭主窗口，悬浮球标志位 = ,{self.is_floating_ball_visible}")
        event.ignore()
        self.hide()
        self.tray_menu.tray_icon.show()

        if not self.is_floating_ball_visible:
            self.create_floating_ball()
        logger.info(f"成功关闭主窗口，悬浮球标志位 = {self.is_floating_ball_visible}")

    def create_floating_ball(self):
        logger.info("---- 创建悬浮球 ----")
        self.floating_ball.show()
        self.is_floating_ball_visible = True


    # 双击托盘，打开窗口
    def tray_icon_activated(self, reason=None):
        logger.info(f"托盘图标激活事件，原因: {reason}")

        # 悬浮球退出
        self.floating_ball.close()
        self.is_floating_ball_visible = False
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            logger.info("---- 双击任务栏托盘，打开窗口 ----")
            self.show()

    def closeEvent(self, event):
        self.handle_close_event(event)


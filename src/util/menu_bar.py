from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenuBar, QMenu

from src.about_window import AboutWindow
from src.const.fs_constants import FsConstants
import os

from src.log_window import LogWindow
from src.option_general import OptionGeneral
from src.option_tab import OptionTab
from loguru import logger



class MenuBar:
    def __init__(self, parent):
        self.parent = parent
        self.menu_bar = QMenuBar(self.parent)
        # 初始化日志窗口
        self.log_window = LogWindow()
        # 初始化首选项窗口
        self.option_tab = OptionTab()
        self._create_help_menu()
        self.about_window = AboutWindow()

    def _create_help_menu(self):
        """创建帮助菜单"""
        help_menu = QMenu(FsConstants.TOOLBAR_HELP_TITLE, self.parent)


        # 创建首选项菜单项
        option_tab_action = QAction("首选项", self.parent)
        option_tab_action.triggered.connect(self.show_option_tab)
        # 创建日志窗口菜单项
        open_log_action = QAction("日志", self.parent)
        open_log_action.triggered.connect(self.show_log_window)

        # 创建日志窗口菜单项
        about_action = QAction("关于", self.parent)
        about_action.triggered.connect(self.show_about_window)

        # 将菜单项添加到“帮助”菜单中
        help_menu.addAction(option_tab_action)
        help_menu.addAction(open_log_action)
        help_menu.addAction(about_action)


        # 添加帮助菜单到菜单栏
        self.menu_bar.addMenu(help_menu)

        # 设置菜单栏
        self.parent.setMenuBar(self.menu_bar)



    def show_log_window(self):
        """显示日志窗口"""
        self.log_window.show()

    def show_option_tab(self):
        """显示首选项窗口"""
        self.option_tab.show()

    def show_about_window(self):
        self.about_window.show()


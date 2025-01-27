from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenuBar, QMenu
from fs_base.base_menu_bar import BaseMenuBar

from src.about_window import AboutWindow
from src.log_window import LogWindow
from src.option_tab import OptionTab



class MenuBar(BaseMenuBar):
    def __init__(self, parent):
        super().__init__(parent)
        self.log_window = LogWindow()
        self.option_tab = OptionTab()
        self.about_window = AboutWindow()

    def show_log_window(self):
        """显示日志窗口"""
        self.log_window.show()

    def show_option_tab(self):
        """显示首选项窗口"""
        self.option_tab.show()

    def show_about_window(self):
        self.about_window.show()

